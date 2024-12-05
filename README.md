# VoiceChatAI 🎙️


VoiceChatAI is an interactive voice-based chatbot that combines speech recognition, natural language processing, and text-to-speech synthesis to create seamless voice conversations. Built with DialoGPT-medium, it offers context-aware responses and natural conversation flow.


## ✨ Features

- **Real-time Voice Interaction**: Seamless speech-to-text and text-to-speech conversion
- **Context-Aware Responses**: Maintains conversation history for coherent dialogue
- **Multiple Voice Options**: Choose between male and female text-to-speech voices
- **Modern UI**: Clean interface with audio visualization and playback controls
- **Speed Control**: Adjust playback speed for generated responses
- **Cross-Platform**: Works on all modern browsers and devices

## 🤔 Why This Tech Stack?
- This project was originally built as part of a hackathon, emphasizing speed, simplicity, and accessibility. To keep the proof-of-concept (POC) free and lightweight:
  - LLM Choice: The DialoGPT-medium model was selected to provide reasonable conversation flow without incurring costs associated with premium models like GPT-4 or Claude. Upgrading to such models could significantly enhance response quality but would require API keys and a paid subscription.
  - TTS Engine: Whisper-small and fast text-to-speech (TTS) was chosen for its balance between speed and accuracy, ensuring quick responses even on standard compute resources. For more accurate and expressive speech synthesis, heavier or paid options could be explored in the future.


## 🛠️ Tech Stack

- **Frontend**:
  - HTML5, CSS3, JavaScript
  - WaveSurfer.js for audio visualization
  - Modern glass-morphism design

- **Backend**:
  - Python 3.8+
  - Flask for API endpoints
  - DialoGPT-medium for conversation
  - pyttsx3 for text-to-speech

## 🚀 Quick Start

1. Clone the repository:
```bash
git clone https://github.com/arshDeepTech/VoiceChatAI.git
```
2. Install dependencies:
```bash
cd VoiceChatAI
conda create --name voicechatai_env python=3.9 numba inflect -y
source activate voicechatai_env
pip install -r requirements.txt
```
3. Start the server:
```bash
python backend/app.py
```


4. Open `http://localhost:5000` in your browser

## 💡 Usage

1. Click the microphone button to start recording
2. Speak your message
3. Wait for the AI response
4. Use playback controls to:
   - Adjust playback speed
   - Play/pause response
   - Stop playback

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

Distributed under the MIT License. See `LICENSE` for more information.

## 👤 Contact

Arsh Deep - [@arshDeepTech](https://github.com/arshDeepTech)

Project Link: [https://github.com/arshDeepTech/VoiceChatAI](https://github.com/arshDeepTech/VoiceChatAI)

## 🙏 Acknowledgments

- [DialoGPT](https://huggingface.co/microsoft/DialoGPT-medium) by Microsoft
- [WaveSurfer.js](https://wavesurfer-js.org/) for audio visualization
- [Flask](https://flask.palletsprojects.com/) for the backend framework
