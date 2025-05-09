import os
import logging
from telegram import Update
from telegram.ext import (
    Application,
    MessageHandler,
    filters,
    ContextTypes,
)

# Configuration
TOKEN = os.environ.get('TOKEN')
CHAT_ID = os.environ.get('CHAT_ID')
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    file = None
    file_size = 0
    
    # Check different file types
    if message.document:
        file = message.document
    elif message.photo:
        file = message.photo[-1]  # Largest photo size
    elif message.video:
        file = message.video
    elif message.audio:
        file = message.audio
    else:
        return
    
    file_size = file.file_size
    
    if file_size > MAX_FILE_SIZE:
        await message.reply_text("❌ File exceeds 5MB limit!")
        return
    
    try:
        # Forward file to target chat
        await context.bot.send_document(
            chat_id=CHAT_ID,
            document=file.file_id,
            caption=f"From: @{message.from_user.username}\nOriginal Chat: {message.chat.id}"
        )
        await message.reply_text("✅ File forwarded successfully!")
    except Exception as e:
        logging.error(f"Error forwarding file: {e}")
        await message.reply_text("❌ Failed to forward file.")

def main():
    # Create Application
    application = Application.builder().token(TOKEN).build()
    
    # Add handler for files
    application.add_handler(MessageHandler(
        filters.Document.ALL | filters.PHOTO | filters.VIDEO | filters.AUDIO,
        handle_file
    ))
    
    # Webhook configuration for Render
    port = int(os.environ.get('PORT', 5000))
    webhook_url = os.environ.get('WEBHOOK_URL')
    
    if webhook_url:
        application.run_webhook(
            listen="0.0.0.0",
            port=port,
            url_path=TOKEN,
            webhook_url=f"{webhook_url}/{TOKEN}"
        )
    else:
        application.run_polling()

if __name__ == "__main__":
    main()