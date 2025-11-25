import instaloader
import os
import shutil

def reproduce():
    target = "downloads\\test_uuid"
    print(f"Target: {target}")
    
    # Create dummy post object (we can't easily mock Post without downloading, 
    # but we can check how Instaloader sanitizes target names if we can access the internal method or just try to download something small if possible, 
    # or just rely on the fact that we saw the issue in logs)
    
    # Actually, let's just check what happens if we create a directory with that name using Instaloader's logic if accessible,
    # or just try to download a public post.
    
    L = instaloader.Instaloader()
    
    # We need a real shortcode to test download_post
    # Let's use a very old/popular post or just trust the user's log.
    # User log showed: downloads﹨ed9da626...
    
    # Let's try to simulate what we think is happening:
    # If we pass "downloads\test" to a function that sanitizes filenames...
    
    sanitized = target.replace('/', '_').replace('\\', '﹨')
    print(f"Hypothetical sanitized: {sanitized}")
    
    if os.path.exists(sanitized):
        print(f"Directory {sanitized} exists!")
    else:
        print(f"Directory {sanitized} does not exist.")

    # Let's try to create a directory with that name to see if it's valid on Windows
    try:
        os.makedirs(sanitized, exist_ok=True)
        print(f"Successfully created directory: {sanitized}")
        # Clean up
        os.rmdir(sanitized)
    except Exception as e:
        print(f"Failed to create directory {sanitized}: {e}")

if __name__ == "__main__":
    reproduce()
