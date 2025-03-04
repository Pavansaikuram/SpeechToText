import asyncio
import websockets
import speech_recognition as sr
import io
import wave

def check_wav_format(audio_bytes):
    """Check if the received audio is in correct WAV format."""
    try:
        with wave.open(io.BytesIO(audio_bytes), "rb") as wav_file:
            print(f"Channels: {wav_file.getnchannels()}")
            print(f"Sample Width: {wav_file.getsampwidth()}")
            print(f"Frame Rate: {wav_file.getframerate()}")
    except Exception as e:
        print(f"Error reading WAV file: {e}")

def process_audio(audio_bytes):
    """Process audio and return transcribed text."""
    recognizer = sr.Recognizer()
    check_wav_format(audio_bytes)  # Debug WAV format

    try:
        audio_file = io.BytesIO(audio_bytes)
        with sr.AudioFile(audio_file) as source:
            audio = recognizer.record(source)
        text = recognizer.recognize_google(audio)
        return text
    except sr.UnknownValueError:
        return "Error: Could not understand the audio"
    except sr.RequestError as e:
        return f"Error: API request failed - {str(e)}"
    except Exception as e:
        return f"Error: {str(e)}"

async def process_websocket(websocket):
    async for message in websocket:
        print("Received audio data")
        text = process_audio(message)  # ✅ No await here
        await websocket.send(text)  # ✅ Only await here

async def main():
    server = await websockets.serve(process_websocket, "localhost", 8000)
    print("Starting WebSocket server at ws://localhost:8000")
    await server.wait_closed()

if __name__ == "__main__":
    asyncio.run(main())
