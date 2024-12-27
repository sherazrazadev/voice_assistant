import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, CallbackContext
import requests
import os
import tempfile
import time

# from pydub import AudioSegment

# Replace with your bot's API token from BotFather
TELEGRAM_BOT_TOKEN = "7270830564:AAHVJTD2Kk8vF5N5yttKdM8IAOfDd_TOg3c"
# Replace with your bot's API URL
BOT_API_URL = "https://api.botmer.io/process"  # Example API endpoint
Voice_API_URL = "https://api.botmer.io/record"
# Start command handler
async def start(update: Update, context: CallbackContext):
    await update.message.reply_text("Hello! My name is Botmer")
# Message handler for user input
async def handle_message(update: Update, context: CallbackContext):
    user_message = update.message.text
    user_id = update.message.chat.id
    # Forward the user message to your bot's API
    try:
        response = requests.post(
            BOT_API_URL,
            json={"user_id": user_id, "message": user_message},
            timeout=60
        )
        response_data = response.json()
        bot_reply = response_data.get("reply", "Sorry, I didn't understand that.")
    except Exception as e:
        bot_reply = f"An error occurred: {str(e)}"
    # Reply to the user
    await update.message.reply_text(bot_reply)

# Handle voice messages (no conversion, just forward the file)
async def handle_voice(update: Update, context: CallbackContext):
    # Get the voice message object from the update
    voice = update.message.voice
    file_id = voice.file_id
    
    # Get the file using the Telegram Bot API
    file = await context.bot.get_file(file_id)
    file_path = file.file_path  # URL to download the file
    
    # Download the voice file to a temporary location
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.ogg')  # Assuming it's an OGG file
    await file.download_to_drive(temp_file.name)
    
    # Send the audio file directly to the backend API (no conversion)
    with open(temp_file.name, 'rb') as f:
        files = {'audio': f}
        try:
            # Send the voice file to the backend API for processing
            response = requests.post(Voice_API_URL, files=files, timeout=120)
            # Check if the response is empty or has invalid JSON
            if not response.content:
                await update.message.reply_text("Sorry, I didn't understand that.Please repeat again.")
                return

            response_data = response.json()
            print("Response status code:", response.status_code)

            # Retrieve the response from the backend (audio URL or text response)
            bot_response = response_data.get("response", "Sorry, I didn't understand that.")
            audio_url = response_data.get("audio_url")  # URL to the generated audio
            print("bot audio url", audio_url)
            
            if not audio_url:
                await update.message.reply_text("Sorry, I could not generate a response.")
            else:
                # Send the generated audio URL as a voice message back to the user
                # Download the response MP3 file
                mp3_response = requests.get(audio_url)
                mp3_binary = mp3_response.content

                # Send the MP3 as an audio file directly (without filename)
                await update.message.reply_audio(audio=mp3_binary, filename="Botmer-Voice")

                # await update.message.reply_voice(voice=audio_url)
        except Exception as e:
            await update.message.reply_text(f"An error occurred: {str(e)}")
    
    # # Clean up the temporary file after processing
    # os.remove(temp_file.name)

# Main function to start the bot
def main():
    # Create the Application with your bot's token
    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    # Register command and message handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.VOICE, handle_voice))  # Handle voice messages
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    # Start the bot
    application.run_polling()
# Run the bot in an existing event loop
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except RuntimeError as e:
        if "Cannot close a running event loop" in str(e):
            loop = asyncio.get_event_loop()
            loop.run_until_complete(main())