import os
import atexit
import glob
from pathlib import Path

STATIC_DIR = Path(__file__).parent.parent / 'static'

def cleanup_audio_files():
    """Remove all generated audio files from the static directory"""
    audio_files = glob.glob(str(STATIC_DIR / '*.mp3'))
    audio_files.extend(glob.glob(str(STATIC_DIR / '*.wav')))
    audio_files.extend(glob.glob(str(STATIC_DIR / '*.ogg')))
    
    for file in audio_files:
        try:
            os.remove(file)
            print(f"Cleaned up: {file}")
        except Exception as e:
            print(f"Error cleaning up {file}: {e}")

# Register the cleanup function to run at exit
atexit.register(cleanup_audio_files) 