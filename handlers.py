import os
import logging
from telegram import Update, InputMediaPhoto, InputMediaVideo
from telegram.ext import ContextTypes
from downloader import MediaDownloader

logger = logging.getLogger(__name__)

# Initialize downloader
downloader = MediaDownloader()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Sends a welcome message when the command /start is issued."""
    user = update.effective_user
    await update.message.reply_html(
        rf"Hi {user.mention_html()}! Send me a link from Instagram, TikTok, or YouTube, and I'll download it for you.",
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Sends a help message when the command /help is issued."""
    await update.message.reply_text("Just send me a link! I support Instagram (Posts, Reels, Carousels), TikTok, and YouTube Shorts.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles incoming text messages."""
    text = update.message.text
    
    # Basic URL validation (very simple)
    if not text.startswith("http"):
        # Ignore non-link messages or maybe reply asking for a link
        return

    status_msg = await update.message.reply_text("Downloading... Please wait.")

    try:
        result = downloader.download(text)
        files = result.get('files', [])
        title = result.get('title', 'Media')
        session_dir = result.get('session_dir')

        if not files:
            await status_msg.edit_text("Could not download any media found at that link.")
            return

        caption = f"{title}\n\nDownloaded via @{context.bot.username}"
        
        if len(files) == 1:
            file_path = files[0]
            ext = os.path.splitext(file_path)[1].lower()
            
            if ext in ['.jpg', '.jpeg', '.png', '.webp']:
                await update.message.reply_photo(photo=open(file_path, 'rb'), caption=caption)
            elif ext in ['.mp4', '.mkv', '.mov', '.avi']:
                await update.message.reply_video(video=open(file_path, 'rb'), caption=caption)
            else:
                await update.message.reply_document(document=open(file_path, 'rb'), caption=caption)
        
        else:
            # Handle multiple files (Album)
            media_group = []
            for i, file_path in enumerate(files):
                ext = os.path.splitext(file_path)[1].lower()
                # Only add caption to the first item
                cap = caption if i == 0 else None
                
                if ext in ['.jpg', '.jpeg', '.png', '.webp']:
                    media_group.append(InputMediaPhoto(open(file_path, 'rb'), caption=cap))
                elif ext in ['.mp4', '.mkv', '.mov', '.avi']:
                    media_group.append(InputMediaVideo(open(file_path, 'rb'), caption=cap))
            
            if media_group:
                await update.message.reply_media_group(media=media_group)
            else:
                 await status_msg.edit_text("Downloaded files are not supported media types.")

        # Cleanup
        downloader.cleanup(session_dir)
        await status_msg.delete()

    except Exception as e:
        logger.error(f"Error handling message: {e}")
        await status_msg.edit_text(f"An error occurred: {str(e)}")
