import os
import requests
import telebot

from dotenv import load_dotenv, find_dotenv
from bs4 import BeautifulSoup
from urllib.parse import urljoin


load_dotenv(find_dotenv('.env'))

bot = telebot.TeleBot(os.getenv('TOKEN'))


@bot.message_handler(commands=['start'])
def hello(message):
    bot.send_message(message.chat.id, f"Привіт, {message.from_user.first_name}! \nНадішліть мені URL оголошення, і я "
                                      f"поверну вам його фото.")


@bot.message_handler()
def handle_image_url(message, output_folder='downloaded_images'):

    url = False

    if message.link_preview_options.url.startswith('https://www.olx'):
        url = message.link_preview_options.url

    if url:
        # Send an HTTP request to the provided link
        response = requests.get(url)

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            bot.send_message(message.chat.id, "Progres: 1/4")
            # Parse the HTML content of the webpage
            soup = BeautifulSoup(response.content, 'html.parser')

            # Find all image tags or any other elements that contain image URLs
            img_tags = soup.find_all('img', {'sizes': True})

            # Create the output folder if it doesn't exist
            os.makedirs(output_folder, exist_ok=True)
            bot.send_message(message.chat.id, "Progres: 2/4")
            # Download each image with the 'sizes' attribute
            for i, img_tag in enumerate(img_tags):
                img_url = img_tag['src']
                img_url = urljoin(url, img_url)  # Make sure the URL is absolute

                # Download the image
                img_response = requests.get(img_url)
                if img_response.status_code == 200:
                    # Save the image to a file
                    img_filename = f'image_{i + 1}.jpg'
                    img_path = os.path.join(output_folder, img_filename)
                    with open(img_path, 'wb') as img_file:
                        img_file.write(img_response.content)
                    print(f'Image {i + 1} downloaded successfully.')
                else:
                    bot.send_message(message.chat.id,
                                     f'Failed to download image {i + 1}. Status code: {img_response.status_code}')
            bot.send_message(message.chat.id, "Progres: 3/4")

            media_group = []

            for i, img_tag in enumerate(img_tags):
                photo_path = f'downloaded_images/image_{i + 1}.jpg'
                media_group.append(telebot.types.InputMediaPhoto(media=open(photo_path, 'rb')))
            bot.send_message(message.chat.id, "Progres: 4/4")
            if media_group:
                bot.send_media_group(message.chat.id, media_group)
            else:
                bot.send_message(message.chat.id, "No images to send.")
        else:
            bot.send_message(message.chat.id, f'Failed to retrieve webpage. Status code: {response.status_code}')
    else:
        bot.send_message(message.chat.id, 'У вашому повідомлені немає посилань на OLX')


bot.polling(none_stop=True)