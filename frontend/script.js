// frontend/script.js

const BACKEND_URL = 'http://localhost:5000'; // Update this to match your backend URL

class VoiceChat {
    constructor() {
        // Initialize properties
        this.isRecording = false;
        this.mediaRecorder = null;
        this.audioChunks = [];
        this.audioPlayer = null;
        this.wavesurfer = null;
        this.isPlaying = false;
        this.playbackRate = 1.0;
        this.pitch = 1.0;

        // Get DOM elements
        this.elements = {
            recordButton: document.getElementById('record-button'),
            uploadButton: document.getElementById('upload-button'),
            messageInput: document.getElementById('message-input'),
            chatMessages: document.getElementById('chat-messages'),
            recordingIndicator: document.getElementById('recording-indicator'),
            audioPlayer: document.getElementById('audio-player'),
            waveform: document.getElementById('waveform'),
            voiceSelector: document.getElementById('voiceType'),
            playButton: document.querySelector('.play-button'),
            speedUp: document.getElementById('speed-up'),
            speedDown: document.getElementById('speed-down'),
            stopButton: document.getElementById('stop-button'),
            speedDisplay: document.querySelector('.speed-display'),
            timeDisplay: document.querySelector('.time-display'),
        };

        // Initialize WaveSurfer
        this.initWaveSurfer();
        
        // Setup event listeners
        this.setupEventListeners();
    }

    initWaveSurfer() {
        this.wavesurfer = WaveSurfer.create({
            container: '#waveform',
            waveColor: '#4a9eff',
            progressColor: '#0084ff',
            cursorColor: '#999',
            height: 40,
            responsive: true,
            barWidth: 2,
            barGap: 3,
            barRadius: 3
        });
    }

    setupEventListeners() {
        // Record button click handler
        this.elements.recordButton.addEventListener('click', () => this.toggleRecording());

        // Upload button click handler
        this.elements.uploadButton.addEventListener('click', () => this.uploadAudio());

        // Message input handler
        this.elements.messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.sendMessage(this.elements.messageInput.value);
            }
        });

        this.elements.speedUp.addEventListener('click', () => this.adjustSpeed(0.25));
        this.elements.speedDown.addEventListener('click', () => this.adjustSpeed(-0.25));
        this.elements.stopButton.addEventListener('click', () => this.stopAudio());
    }

    async toggleRecording() {
        if (!this.isRecording) {
            try {
                const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                this.startRecording(stream);
            } catch (err) {
                console.error('Error accessing microphone:', err);
                this.showError('Please allow microphone access to record audio.');
            }
        } else {
            this.stopRecording();
        }
    }

    startRecording(stream) {
        this.isRecording = true;
        this.audioChunks = [];
        
        this.mediaRecorder = new MediaRecorder(stream);
        
        this.mediaRecorder.ondataavailable = (event) => {
            this.audioChunks.push(event.data);
        };

        this.mediaRecorder.onstop = () => {
            const audioBlob = new Blob(this.audioChunks, { type: 'audio/wav' });
            this.processAudioRecording(audioBlob);
        };

        // Update UI
        this.elements.recordButton.innerHTML = '<i class="fas fa-stop"></i><span>Stop</span>';
        this.elements.recordButton.classList.add('recording');
        this.elements.recordingIndicator.classList.add('active');
        
        this.mediaRecorder.start();
    }

    stopRecording() {
        if (this.mediaRecorder && this.isRecording) {
            this.mediaRecorder.stop();
            this.isRecording = false;
            
            // Update UI
            this.elements.recordButton.innerHTML = '<i class="fas fa-microphone"></i><span>Record</span>';
            this.elements.recordButton.classList.remove('recording');
            this.elements.recordingIndicator.classList.remove('active');
            
            // Stop all tracks
            this.mediaRecorder.stream.getTracks().forEach(track => track.stop());
        }
    }

    async processAudioRecording(audioBlob) {
        try {
            const formData = new FormData();
            formData.append('audio', audioBlob);

            const response = await fetch('/process-audio', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();
            
            if (data.success) {
                this.addMessage(data.transcription, 'user');
                await this.getAIResponse(data.transcription);
            } else {
                this.showError('Error processing audio: ' + data.error);
            }
        } catch (err) {
            console.error('Error processing audio:', err);
            this.showError('Error processing audio recording.');
        }
    }

    async uploadAudio() {
        const input = document.createElement('input');
        input.type = 'file';
        input.accept = 'audio/*';
        
        input.onchange = async (e) => {
            const file = e.target.files[0];
            if (file) {
                const formData = new FormData();
                formData.append('audio', file);
                await this.processAudioRecording(file);
            }
        };
        
        input.click();
    }

    async sendMessage(text) {
        if (!text.trim()) return;
        
        this.elements.messageInput.value = '';
        this.addMessage(text, 'user');
        await this.getAIResponse(text);
    }

    async getAIResponse(text) {
        try {
            const response = await fetch('/get-response', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    text: text,
                    voice: this.elements.voiceSelector.value
                })
            });

            const data = await response.json();
            
            if (data.success) {
                this.addMessage(data.response, 'bot');
                if (data.audio_url) {
                    this.playAudioResponse(data.audio_url);
                }
            } else {
                this.showError('Error getting response: ' + data.error);
            }
        } catch (err) {
            console.error('Error getting AI response:', err);
            this.showError('Error getting AI response.');
        }
    }

    addMessage(text, type) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}-message`;
        
        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';

        if (type === 'bot') {
            const icon = document.createElement('i');
            icon.className = 'fas fa-robot bot-icon';
            contentDiv.appendChild(icon);
        }

        const textP = document.createElement('p');
        textP.textContent = text;
        contentDiv.appendChild(textP);
        
        messageDiv.appendChild(contentDiv);
        this.elements.chatMessages.appendChild(messageDiv);
        this.elements.chatMessages.scrollTop = this.elements.chatMessages.scrollHeight;
    }

    playAudioResponse(audioUrl) {
        this.wavesurfer.load(audioUrl);
        this.elements.audioPlayer.classList.add('active');
        
        // Reset playback settings
        this.playbackRate = 1.0;
        this.elements.speedDisplay.textContent = '1.00x';
        
        const playButton = this.elements.audioPlayer.querySelector('.play-button');
        
        this.wavesurfer.on('ready', () => {
            this.wavesurfer.play();
            this.isPlaying = true;
            playButton.innerHTML = '<i class="fas fa-pause"></i>';
        });

        this.wavesurfer.on('finish', () => {
            this.isPlaying = false;
            playButton.innerHTML = '<i class="fas fa-play"></i>';
        });

        this.wavesurfer.on('audioprocess', () => {
            this.elements.timeDisplay.textContent = formatTime(this.wavesurfer.getCurrentTime());
        });

        playButton.onclick = () => {
            if (this.isPlaying) {
                this.wavesurfer.pause();
                this.isPlaying = false;
                playButton.innerHTML = '<i class="fas fa-play"></i>';
            } else {
                this.wavesurfer.play();
                this.isPlaying = true;
                playButton.innerHTML = '<i class="fas fa-pause"></i>';
            }
        };
    }

    showError(message) {
        // Add error message to chat
        this.addMessage(`Error: ${message}`, 'bot');
    }

    adjustSpeed(delta) {
        this.playbackRate = Math.max(0.5, Math.min(2, this.playbackRate + delta));
        this.wavesurfer.setPlaybackRate(this.playbackRate);
        this.elements.speedDisplay.textContent = `${this.playbackRate.toFixed(2)}x`;
    }

    stopAudio() {
        this.wavesurfer.stop();
        this.isPlaying = false;
        this.elements.playButton.innerHTML = '<i class="fas fa-play"></i>';
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new VoiceChat();
});

// Add this at the end of your script.js
document.getElementById('currentYear').textContent = new Date().getFullYear();

// Helper function to format time
function formatTime(seconds) {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = Math.floor(seconds % 60);
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
}
