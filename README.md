# Speech-to-Text WebSocket Application

This project enables real-time speech-to-text conversion using Python, WebSockets, and Streamlit. The application records audio from the user's microphone, sends it to a WebSocket server, and receives transcribed text in real time.

## Features
- Record speech from the microphone.
- Send recorded audio to a WebSocket server.
- Transcribe speech to text using Google Speech Recognition.
- Display transcribed text in a Streamlit UI.

## Requirements
Ensure you have Python installed. Then, install the required dependencies:

```sh
pip install -r requirements.txt
```

## File Structure
- `app.py`: Streamlit application to record audio and display transcribed text.
- `stream.py`: WebSocket server that processes and transcribes audio.

## Usage
### 1. Start the WebSocket Server
Run the WebSocket server to process incoming audio:
```sh
python stream.py
```

### 2. Start the Streamlit Application
Run the Streamlit application to record and transcribe speech:
```sh
streamlit run app.py
```

## Troubleshooting
### WebSocket Connection Errors
Ensure the WebSocket server (`stream.py`) is running before starting the Streamlit app.

### Microphone Not Detected
If your microphone is not detected, check your system's audio settings and permissions.

### Audio Format Errors
Ensure the recorded audio is in the correct format (PCM WAV, AIFF, or Native FLAC). If issues persist, debug using the `check_wav_format` function in `stream.py`.

## Future Enhancements
- Enable continuous listening for real-time transcription.
- Improve UI with better real-time updates.
- Support for multiple languages.
