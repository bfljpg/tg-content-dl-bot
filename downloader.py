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

        try:
            if "instagram.com" in url:
                return self._download_instagram(url, session_dir)
            else:
                return self._download_ytdlp(url, session_dir)

        except Exception as e:
            logger.error(f"Download failed: {e}")
            # Cleanup on failure
            if os.path.exists(session_dir):
                shutil.rmtree(session_dir)
            raise e

    def _download_instagram(self, url: str, session_dir: str) -> Dict:
        import instaloader
        import re

        # Extract shortcode
        shortcode_match = re.search(r'(?:p|reel|tv)/([A-Za-z0-9_-]+)', url)
        if not shortcode_match:
            raise ValueError("Could not extract Instagram shortcode from URL.")
        shortcode = shortcode_match.group(1)

        # Configure Instaloader
        L = instaloader.Instaloader(
            download_pictures=True,
            download_videos=True,
            download_video_thumbnails=False,
            download_geotags=False,
            download_comments=False,
            save_metadata=False,
            compress_json=False,
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )

        # Session loading logic removed as per request


        # Download
        try:
            post = instaloader.Post.from_shortcode(L.context, shortcode)
            # Instaloader downloads to a directory named after the target. 
            # We pass session_dir as the target.
            L.download_post(post, target=session_dir)
        except Exception as e:
            logger.warning(f"Instaloader raised an error: {e}. Checking if files were downloaded anyway...")

        # Gather files (filter out non-media)
        files = []
        for root, dirs, filenames in os.walk(session_dir):
            for filename in filenames:
                if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.mp4')):
                    files.append(os.path.abspath(os.path.join(root, filename)))
        
        # Remove txt files if any (captions)
        for root, dirs, filenames in os.walk(session_dir):
            for filename in filenames:
                if filename.lower().endswith('.txt'):
                    os.remove(os.path.join(root, filename))

        if not files:
            raise Exception("No media files downloaded from Instagram.")

        return {
            'files': files,
            'title': f"Instagram Post {shortcode}",
            'session_dir': session_dir
        }

    def _download_ytdlp(self, url: str, session_dir: str) -> Dict:
        ydl_opts = {
            'outtmpl': os.path.join(session_dir, '%(title)s.%(ext)s'),
            'quiet': True,
            'no_warnings': True,
            'ignoreerrors': True,
            # Use cookies from the default browser (Chrome) to bypass login requirements
            'cookiesfrombrowser': ('chrome',), 
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            
            if 'entries' in info:
                title = info.get('title', 'Downloaded Content')
            else:
                title = info.get('title', 'Downloaded Content')

        files = []
        for root, dirs, filenames in os.walk(session_dir):
            for filename in filenames:
                files.append(os.path.abspath(os.path.join(root, filename)))

        if not files:
            raise Exception("No files downloaded.")

        return {
            'files': files,
            'title': title,
            'session_dir': session_dir
        }

    def cleanup(self, session_dir: str):
        """Removes the session directory and its contents."""
        if os.path.exists(session_dir):
            shutil.rmtree(session_dir)
