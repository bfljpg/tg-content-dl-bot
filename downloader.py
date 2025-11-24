import os
import glob
import uuid
import shutil
import logging
from typing import List, Dict, Optional
import yt_dlp

logger = logging.getLogger(__name__)

class MediaDownloader:
    def __init__(self, download_dir: str = "downloads"):
        self.download_dir = download_dir
        if not os.path.exists(self.download_dir):
            os.makedirs(self.download_dir)

    def download(self, url: str) -> Dict:
        """
        Downloads media from the given URL.
        Returns a dictionary containing:
        - 'files': List of absolute paths to downloaded files.
        - 'title': Title of the content.
        - 'type': 'video', 'image', or 'mixed'.
        """
        # Create a unique sub-directory for this download to avoid collisions
        session_id = str(uuid.uuid4())
        session_dir = os.path.join(self.download_dir, session_id)
        os.makedirs(session_dir, exist_ok=True)

        ydl_opts = {
            'outtmpl': os.path.join(session_dir, '%(title)s.%(ext)s'),
            'quiet': True,
            'no_warnings': True,
            'ignoreerrors': True,
            # 'format': 'bestvideo+bestaudio/best', # Default is usually good enough
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                
                # If it's a playlist or carousel, 'entries' will be present
                if 'entries' in info:
                    title = info.get('title', 'Downloaded Content')
                    # We might want to look at the first entry for more info if needed
                else:
                    title = info.get('title', 'Downloaded Content')

            # Gather downloaded files
            files = []
            for root, dirs, filenames in os.walk(session_dir):
                for filename in filenames:
                    files.append(os.path.abspath(os.path.join(root, filename)))

            if not files:
                raise Exception("No files downloaded.")

            return {
                'files': files,
                'title': title,
                'session_dir': session_dir # Return this so we can cleanup later
            }

        except Exception as e:
            logger.error(f"Download failed: {e}")
            # Cleanup on failure
            if os.path.exists(session_dir):
                shutil.rmtree(session_dir)
            raise e

    def cleanup(self, session_dir: str):
        """Removes the session directory and its contents."""
        if os.path.exists(session_dir):
            shutil.rmtree(session_dir)
