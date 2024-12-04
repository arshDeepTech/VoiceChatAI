# backend/app.py
import os
import asyncio
from flask import Flask, request, jsonify, send_from_directory, send_file, session
from whisper_model import transcribe_audio
from tts_model import generate_speech
from datetime import datetime, timedelta
import io
from scipy.io.wavfile import write
import numpy as np
from flask_cors import CORS
from pathlib import Path
from utils.cleanup import cleanup_audio_files
import atexit
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
from collections import deque
import random
import uuid
import secrets
import logging

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)  # Generate a secure secret key
app.config['SESSION_TYPE'] = 'filesystem'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=1)  # Session expires after 1 day
CORS(app, resources={
    r"/*": {
        "origins": "*",
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

# Define absolute paths
BASE_DIR = Path(__file__).parent.parent
FRONTEND_DIR = BASE_DIR / 'frontend'
STATIC_DIR = BASE_DIR / 'backend' / 'static'
AUDIO_DIR = STATIC_DIR / 'audio'

# Ensure directories exist
AUDIO_DIR.mkdir(parents=True, exist_ok=True)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ChatBot:
    def __init__(self):
        logger.info("Initializing DialoGPT-medium model...")
        try:
            # Initialize model and tokenizer
            self.model = AutoModelForCausalLM.from_pretrained("microsoft/DialoGPT-medium")
            self.tokenizer = AutoTokenizer.from_pretrained("microsoft/DialoGPT-medium")
            
            # Move model to GPU if available
            if torch.cuda.is_available():
                self.model = self.model.cuda()
                logger.info("Model loaded on GPU")
            else:
                logger.info("Model loaded on CPU")
            
            # Maintain conversation history
            self.max_history = 5
            self.conversations = {}
            
            # Add personality and variety
            self.conversation_starters = [
                "I understand. ",
                "That's interesting. ",
                "Let me think about that. ",
                "I see what you mean. ",
                "Here's what I think: ",
                "From my perspective, ",
            ]
            
        except Exception as e:
            logger.error(f"Error initializing model: {str(e)}")
            raise

    def get_response(self, user_id, text):
        try:
            # Get or create conversation history for this user
            if user_id not in self.conversations:
                self.conversations[user_id] = deque(maxlen=self.max_history)
                
            history = self.conversations[user_id]
            
            # Add user input to history
            encoded_input = self.tokenizer.encode(text + self.tokenizer.eos_token, return_tensors='pt')
            if torch.cuda.is_available():
                encoded_input = encoded_input.cuda()
            history.append(encoded_input)
            
            # Combine history into a single input
            bot_input_ids = torch.cat(list(history), dim=-1)
            
            # Generate response with some randomness
            response_ids = self.model.generate(
                bot_input_ids,
                max_length=1000,
                pad_token_id=self.tokenizer.eos_token_id,
                no_repeat_ngram_size=3,
                do_sample=True,
                top_k=50,
                top_p=0.95,
                temperature=0.7,
                num_beams=5,
                early_stopping=True
            )
            
            # Decode and clean up response
            response = self.tokenizer.decode(
                response_ids[:, bot_input_ids.shape[-1]:][0],
                skip_special_tokens=True
            )
            
            # Add variety with conversation starters (20% chance)
            if random.random() < 0.2:
                starter = random.choice(self.conversation_starters)
                response = f"{starter}{response}"
                
            # Clean up response
            response = response.strip()
            if not response:
                response = "I understand. Please continue."
            
            # Add response to history
            encoded_response = self.tokenizer.encode(
                response + self.tokenizer.eos_token,
                return_tensors='pt'
            )
            if torch.cuda.is_available():
                encoded_response = encoded_response.cuda()
            history.append(encoded_response)
            
            return response
            
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            return "I apologize, but I'm having trouble processing that right now."

# Initialize chatbot
chatbot = ChatBot()

@app.route('/')
def serve_frontend():
    return send_from_directory(FRONTEND_DIR, 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    # First try to serve from frontend directory
    frontend_file = FRONTEND_DIR / path
    if frontend_file.exists():
        return send_from_directory(FRONTEND_DIR, path)
    
    # Then try to serve from static directory
    static_file = STATIC_DIR / path
    if static_file.exists():
        return send_from_directory(STATIC_DIR, path)
    
    return "File not found", 404

@app.route('/process-audio', methods=['POST'])
def process_audio():
    try:
        if 'audio' not in request.files:
            return jsonify({'error': 'No audio file provided'}), 400

        audio_file = request.files['audio']
        
        # Save the audio file temporarily
        temp_path = 'temp_audio.wav'
        audio_file.save(temp_path)
        
        # Transcribe the audio using Whisper
        transcription = transcribe_audio(temp_path)
        
        # Clean up the temporary file
        os.remove(temp_path)
        
        return jsonify({
            'success': True,
            'transcription': transcription
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/get-response', methods=['POST'])
def get_response():
    try:
        data = request.json
        text = data.get('text')
        voice_type = data.get('voice', 'female')
        
        if not text:
            return jsonify({'error': 'No text provided'}), 400
            
        # Get user ID from session or create new one
        user_id = session.get('user_id', str(uuid.uuid4()))
        session['user_id'] = user_id
        
        # Get response from chatbot
        response_text = chatbot.get_response(user_id, text)
        
        try:
            # Generate speech
            audio_path = generate_speech(response_text, voice_type)
            
            if not os.path.exists(audio_path):
                raise Exception("Audio file was not generated")
                
            # Get just the filename for the URL
            audio_filename = os.path.basename(audio_path)
            audio_url = f'/static/audio/{audio_filename}'
            
            return jsonify({
                'success': True,
                'response': response_text,
                'audio_url': audio_url
            })
            
        except Exception as e:
            app.logger.error(f"TTS Error: {str(e)}")
            return jsonify({
                'success': True,
                'response': response_text,
                'error': str(e)
            })
            
    except Exception as e:
        app.logger.error(f"Error in get_response: {str(e)}")
        return jsonify({'error': str(e)}), 500

# Serve static files (generated audio)
@app.route('/static/audio/<filename>')
def serve_audio(filename):
    try:
        return send_from_directory(AUDIO_DIR, filename, mimetype='audio/wav')
    except Exception as e:
        app.logger.error(f"Error serving audio file: {str(e)}")
        return jsonify({'error': str(e)}), 404

if __name__ == '__main__':
    # Register cleanup on exit
    atexit.register(cleanup_audio_files)
    app.run(debug=True, port=5000)
