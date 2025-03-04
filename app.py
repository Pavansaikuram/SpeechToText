import streamlit as st
import asyncio
import websockets
import pyaudio
import wave
import io

# WebSocket Server URL
WEBSOCKET_SERVER = "ws://localhost:8000"

# Audio settings
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000  # Ensure it matches the server's expected format
CHUNK = 1024


# Function to record audio
def record_audio(duration=5):
    """Records audio from the microphone for the given duration."""
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)

    st.info("Recording... Speak now!")
    frames = []

    for _ in range(0, int(RATE / CHUNK * duration)):
        data = stream.read(CHUNK)
        frames.append(data)

    st.success("Recording complete! Processing...")

    stream.stop_stream()
    stream.close()
    p.terminate()

    # Convert recorded frames to a WAV file format
    wav_buffer = io.BytesIO()
    with wave.open(wav_buffer, 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))

    return wav_buffer.getvalue()


# Function to send audio to WebSocket server
async def send_audio(audio_data):
    """Sends recorded audio to WebSocket server and receives transcribed text."""
    try:
        async with websockets.connect(WEBSOCKET_SERVER) as websocket:
            await websocket.send(audio_data)  # Send audio bytes
            response = await websocket.recv()  # Receive response
            return response
    except Exception as e:
        return f"Error: {str(e)}"


# Streamlit UI
st.title("Live Speech-to-Text with WebSockets")
st.write("Click the button to record and transcribe your speech.")

if st.button("Record and Transcribe"):
    audio_data = record_audio(duration=5)  # Record 5 seconds of speech
    text = asyncio.run(send_audio(audio_data))  # Send to WebSocket & get response
    st.text_area("Transcribed Text:", text)
