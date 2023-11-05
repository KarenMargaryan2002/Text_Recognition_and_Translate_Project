# Importing the necessary modules and packages
# import json
import requests
import telebot
from gtts import gTTS
# from tempfile import NamedTemporaryFile
from telebot import types

check = 0

def checker():
    global check
    check = 0

# Function to display the options as buttons
def display_options(chat_id):
    global check
    if check != 0:
        return
    # Create the inline keyboard
    keyboard = types.InlineKeyboardMarkup()

    # Create the translate button
    translate_button = types.InlineKeyboardButton(
        text="Translate: hy -> en", callback_data="translate"
    )
    keyboard.add(translate_button)

    # Create the image-to-text button
    image_button = types.InlineKeyboardButton(
        text="Image to text", callback_data="image"
    )
    keyboard.add(image_button)

    # Send the options to the user
    bot.send_message(chat_id, "Please choose an option:", reply_markup=keyboard)


# Initialize the Telegram bot using your bot token
bot = telebot.TeleBot("6367178485:AAFz26v5Df4qPvU_pN29G0RSOPkMYCfXj3Q")

# Handler for /start and /hello commands
@bot.message_handler(commands=["start", "hello"])
def send_welcome(message):
    # Send a welcome message to the user
    bot.reply_to(
        message, "Welcome to the bot! Please select an option from the buttons below."
    )
    # Call the function to display the options
    display_options(message.chat.id)

# Handler for all other messages
@bot.message_handler()
def send_welcome(message):
    # Send a default response for unknown messages
    bot.reply_to(
        message,
        "I'm sorry, but I didn't understand that. Please select an option from the buttons below.",
    )
    # Call the function to display the options
    display_options(message.chat.id)

# Callback handler for button clicks
@bot.callback_query_handler(func=lambda call: True)
def handle_button_click(call):
    # Check the callback data and take appropriate action
    if call.data == "translate":
        translate_hy_to_en(call.message)
    elif call.data == "image":
        image_to_text(call.message)

# Function to handle translation from hy to en
def translate_hy_to_en(message):
    global check
    if check != 0:
        return
    check = 1
    # Ask the user to enter the text to translate
    bot.reply_to(message, "Enter the text to translate:")

    # Handler for translation input
    @bot.message_handler(func=lambda message: True)
    def process_translation(message):
        text = message.text

        # URL for the translation API
        url = "https://rapid-translate-multi-traduction.p.rapidapi.com/t"

        # Define the payload (data) for the translation request
        payload = {"q": text, "to": "en", "from": "hy"}

        # Define the headers for the API request
        headers = {
            "content-type": "application/json",
            "X-RapidAPI-Key": "9d22f32413mshdb9880a804a0e23p194114jsn20efbd9b95f5",
            "X-RapidAPI-Host": "rapid-translate-multi-traduction.p.rapidapi.com"
        }

        # Send a POST request to the translation API
        try:
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            bot.reply_to(message, "Translation request failed. Please try again later.")
            checker()
            display_options(message.chat.id)
            return

        # Get the translated text from the response
        try:
            translated_text = response.json()[0]
        except (KeyError, ValueError):
            bot.reply_to(message, "Translation error. Please try again.")
            checker()
            display_options(message.chat.id)
            return

        # Reply with the translated text
        bot.reply_to(message, translated_text)
        # Convert the translated text to speech
        convert_text_to_speech(translated_text, message.chat.id)
        # Display the options again
        checker()
        display_options(message.chat.id)
        return

    # Register the next step handler for translation input
    bot.register_next_step_handler(message, process_translation)

# Function to handle image-to-text conversion
def image_to_text(message):
    global check
    if check != 0:
        return
    check = 2
    # Ask the user to upload the image
    bot.reply_to(message, "Please upload the image.")

    # Handler for image upload
    # Uncomment the decorator below if you want to handle image uploads
    # @bot.message_handler(content_types=["photo"])
    def process_image(message):
        try:
            file_id = message.photo[-1].file_id
        except:
            bot.reply_to(message, "Photo upload error. Please upload photo again.")
            checker()
            display_options(message.chat.id)
            return

        file_info = bot.get_file(file_id)
        file_url = f"https://api.telegram.org/file/bot{bot.token}/{file_info.file_path}"

        url = "https://microsoft-computer-vision3.p.rapidapi.com/ocr"

        querystring = {"detectOrientation": "true", "language": "unk"}

        payload = {"url": file_url}

        headers = {
            "content-type": "application/json",
            "X-RapidAPI-Key": "9d22f32413mshdb9880a804a0e23p194114jsn20efbd9b95f5",
            "X-RapidAPI-Host": "microsoft-computer-vision3.p.rapidapi.com",
        }

        try:
            response = requests.post(
                url, json=payload, headers=headers, params=querystring
            )
            response.raise_for_status()
        except:
            bot.reply_to(
                message, "Image-to-text conversion failed. Please try again later."
            )
            checker()
            display_options(message.chat.id)
            return

        try:
            text = ""
            for region in response.json()["regions"]:
                for line in region["lines"]:
                    for word in line["words"]:
                        text += word["text"] + " "
                        if text.endswith(". "):
                            text += "\n"
        except (KeyError, ValueError):
            bot.reply_to(message, "Image-to-text conversion error. Please try again.")
            checker()
            display_options(message.chat.id)
            return

        try:
            # bot.reply_to(message, text)
            if len(text) > 4095:
                for x in range(0, len(text), 4095):
                    bot.reply_to(message, text=text[x:x+4095])
            else:
                bot.reply_to(message, text)

            convert_text_to_speech(text, message.chat.id)
        except:
            bot.reply_to(message, "Image-to-text conversion error. Please try again.")
            pass
        checker()
        display_options(message.chat.id)
        return

    # Register the next step handler for image upload
    bot.register_next_step_handler(message, process_image)

# Function to convert text to speech and send as audio
def convert_text_to_speech(text, chat_id):
    tts = gTTS(text=text, lang="en", slow=False)

    filename = "my_audio.mp3"

    tts.save(filename)

    with open(filename, "rb") as audio_file:
        bot.send_audio(chat_id, audio_file)





# Start the bot
checker()
bot.polling()