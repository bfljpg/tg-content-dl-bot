import yt_dlp
import os

def test_ytdlp():
    url = "https://www.youtube.com/shorts/test_video" # Dummy URL, we just want to see if it initializes/loads cookies
    
    # Options from downloader.py
    ydl_opts = {
        'quiet': False, # Enable output to see errors
        'no_warnings': False,
        'ignoreerrors': True,
        'cookiesfrombrowser': ('chrome',), 
    }

    print("Attempting to initialize yt-dlp with chrome cookies...")
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # We don't need to actually download to trigger the cookie load, 
            # usually it happens on initialization or first extraction.
            # Let's try to extract info for a safe public video or just the dummy.
            # Using a real public video ID might be better to test if it works without cookies too.
            # But for now let's just see the cookie error.
            print("yt-dlp initialized.")
            # ydl.extract_info(url, download=False) 
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_ytdlp()
