import os
from dotenv import load_dotenv, find_dotenv

import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters


import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

load_dotenv(find_dotenv('.env'))

TOKEN = os.getenv('TOKEN')


def start(update, context):
    update.message.reply_text("Привіт! Надішліть мені URL OLX, і я поверну вам його вміст.")


def handle_image_url(update, context, output_folder='downloaded_images'):
    url = update.message.text
    print(url)
    # Send an HTTP request to the provided link
    response = requests.get(url)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Parse the HTML content of the webpage
        soup = BeautifulSoup(response.content, 'html.parser')

        # Find all image tags or any other elements that contain image URLs
        img_tags = soup.find_all('img', {'sizes': True})

        # Create the output folder if it doesn't exist
        os.makedirs(output_folder, exist_ok=True)

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
                update.message.reply_text(f'Image {i + 1} downloaded successfully.')
            else:
                update.message.reply_text(f'Failed to download image {i + 1}. Status code: {img_response.status_code}')

        for i, img_tag in enumerate(img_tags):
            update.message.reply_photo(photo=open(f'downloaded_images/image_{i + 1}.jpg', 'rb'))
    else:
        update.message.reply_text(f'Failed to retrieve webpage. Status code: {response.status_code}')

if __name__ == '__main__':
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_image_url))

    updater.start_polling()
    updater.idle()