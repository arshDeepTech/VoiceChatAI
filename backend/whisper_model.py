# backend/whisper_model.py
import whisper

# Load the Whisper model (use a smaller model for performance)
model = whisper.load_model("small")

def transcribe_audio(audio_path):
    # Transcribe the uploaded audio file
    result = model.transcribe(audio_path)
    return result['text']
