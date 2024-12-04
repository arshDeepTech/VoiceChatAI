import os
from datetime import datetime
import logging
import pyttsx3
from pathlib import Path
import uuid

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimpleTTS:
    def __init__(self):
        logger.info("Initializing TTS engine...")
        try:
            self.engine = pyttsx3.init()
            # Get available voices
            voices = self.engine.getProperty('voices')
            self.male_voice = voices[0].id
            self.female_voice = voices[1].id if len(voices) > 1 else voices[0].id
            
            # Set default properties
            self.engine.setProperty('rate', 175)  # Speed of speech
            self.engine.setProperty('volume', 1.0)  # Volume
            
            logger.info("TTS engine initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing TTS engine: {str(e)}")
            raise

    def generate_speech(self, text, voice_type='female'):
        """Generate speech from text and save to a file"""
        try:
            if not text:
                raise ValueError("No text provided for speech generation")

            # Configure voice
            voice_id = self.female_voice if voice_type.lower() == 'female' else self.male_voice
            self.engine.setProperty('voice', voice_id)
            
            # Generate unique filename
            filename = f"speech_{uuid.uuid4()}.wav"
            audio_dir = Path(__file__).parent / 'static' / 'audio'
            audio_path = audio_dir / filename
            
            # Ensure directory exists
            audio_dir.mkdir(parents=True, exist_ok=True)
            
            # Save to file
            self.engine.save_to_file(text, str(audio_path))
            self.engine.runAndWait()
            
            if not audio_path.exists():
                raise Exception("Audio file was not generated")
                
            logger.info(f"Successfully generated audio file at {audio_path}")
            return str(audio_path)
            
        except Exception as e:
            logger.error(f"Error generating speech: {str(e)}")
            raise

# Initialize TTS model
tts_model = SimpleTTS()

def generate_speech(text, voice_type='female'):
    """Wrapper function for TTS generation"""
    return tts_model.generate_speech(text, voice_type)