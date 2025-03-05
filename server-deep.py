import asyncio
import json
import ssl
from typing import Dict, Optional, List

import websockets
import websocket

# TODO Remove while Genesys integration
# MediaFormat to hold audio format data
class MediaFormat:
    def __init__(self, encoding: str, sample_rate: int, channels: int):
        self.encoding = encoding
        self.sample_rate = sample_rate
        self.channels = channels

    def __repr__(self):
        return f"MediaFormat(encoding={self.encoding}, sample_rate={self.sample_rate}, channels={self.channels})"

# TODO Remove while Genesys integration
# StartEvent to capture the starting event details
class StartEvent:
    def __init__(self, account_sid: str, stream_sid: str, call_sid: str, tracks: List[str],
                 media_format: MediaFormat, custom_parameters: Optional[Dict] = None):
        self.account_sid = account_sid
        self.stream_sid = stream_sid
        self.call_sid = call_sid
        self.tracks = tracks
        self.media_format = media_format
        self.custom_parameters = custom_parameters if custom_parameters else {}

    def __repr__(self):
        return (f"StartEvent(account_sid={self.account_sid}, stream_sid={self.stream_sid}, "
                f"call_sid={self.call_sid}, tracks={self.tracks}, media_format={self.media_format}, "
                f"custom_parameters={self.custom_parameters})")

# TODO Remove while Genesys integration
# MediaEvent to hold the audio chunk data
class MediaEvent:
    def __init__(self, track: str, chunk: int, timestamp: int, payload: str, stream_sid: str):
        self.track = track
        self.chunk = chunk
        self.timestamp = timestamp
        self.payload = payload
        self.stream_sid = stream_sid

    def __repr__(self):
        return (f"MediaEvent(track={self.track}, chunk={self.chunk}, timestamp={self.timestamp}, "
                f"payload={self.payload}, stream_sid={self.stream_sid})")

# TODO Remove while Genesys integration
# AudioData to store both 'start' and 'media' events
class AudioData:
    def __init__(self, event: str, sequence_number: str, start: Optional[StartEvent] = None,
                 media: Optional[MediaEvent] = None, stream_sid: str = None):
        self.event = event
        self.sequence_number = sequence_number
        self.start = start
        self.media = media
        self.stream_sid = stream_sid

    def __repr__(self):
        return (f"AudioData(event={self.event}, sequence_number={self.sequence_number}, "
                f"start={self.start}, media={self.media}, stream_sid={self.stream_sid})")

    @classmethod
    def from_dict(cls, data: Dict):
        event = data.get('event')
        sequence_number = data.get('sequenceNumber')
        stream_sid = data.get('streamSid')

        if event == 'start' and 'start' in data:
            start_data = data['start']
            media_format = MediaFormat(**start_data['mediaFormat'])
            start_event = StartEvent(
                account_sid=start_data['accountSid'],
                stream_sid=start_data['streamSid'],
                call_sid=start_data['callSid'],
                tracks=start_data['tracks'],
                media_format=media_format,
                custom_parameters=start_data.get('customParameters')
            )
            return cls(event=event, sequence_number=sequence_number, start=start_event, stream_sid=stream_sid)

        if event == 'media' and 'media' in data:
            media_data = data['media']
            media_event = MediaEvent(
                track=media_data['track'],
                chunk=media_data['chunk'],
                timestamp=media_data['timestamp'],
                payload=media_data['payload'],
                stream_sid=stream_sid
            )
            return cls(event=event, sequence_number=sequence_number, media=media_event, stream_sid=stream_sid)

        return cls(event=event, sequence_number=sequence_number, stream_sid=stream_sid)

# WebSocket handler to process incoming WebSocket messages
async def process_websocket(websocket):
    async for message in websocket:
        print("Received audio data:", message)

        # Parse the incoming message
        data = json.loads(message)

        # TODO Remove while Genesys integration
        if data["event"] == "connected":
            print("Connection established:", data)

        elif data["event"] == "start":
            start_data = data.get("start")
            if start_data:
                # Parse the media format from the 'start' event
                media_format = MediaFormat(
                    encoding=start_data["mediaFormat"]["encoding"],
                    sample_rate=start_data["mediaFormat"]["sampleRate"],
                    channels=start_data["mediaFormat"]["channels"]
                )

                start_event = StartEvent(
                    account_sid=start_data["accountSid"],
                    stream_sid=start_data["streamSid"],
                    call_sid=start_data["callSid"],
                    tracks=start_data["tracks"],
                    media_format=media_format,
                    custom_parameters=start_data.get("customParameters", {})
                )

                # Create AudioData object for the 'start' event
                audio_data = AudioData(
                    event=data["event"],
                    sequence_number=data["sequenceNumber"],
                    start=start_event,
                    stream_sid=data["streamSid"]
                )

                # Send the audio data to Deepgram for transcription
                await send_to_deepgram(audio_data)

        elif data["event"] == "media":
            media_data = data.get("media")
            if media_data:
                audio_data = AudioData(
                    event=data["event"],
                    sequence_number=data["sequenceNumber"],
                    media=MediaEvent(
                        track=media_data["track"],
                        chunk=media_data["chunk"],
                        timestamp=media_data["timestamp"],
                        payload=media_data["payload"],
                        stream_sid=data["streamSid"]
                    ),
                    stream_sid=data["streamSid"]
                )
                # Send the audio data to Deepgram for transcription
                await send_to_deepgram(audio_data)

        else:
            print("Unhandled event type:", data["event"])

# Function to send audio data to Deepgram for transcription using WebSocket
# Refactor to use in deepseek.py
async def send_to_deepgram(audio_data):
    print("Transcription sending to Deepgram+++++++:", audio_data)

    # Set up SSL context for connection to Deepgram's WebSocket
    context = ssl._create_unverified_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE

    # WebSocket headers for authentication
    headers = [
        "Authorization: Token REDACTED",  # Replace with your Deepgram API token
        "Content-Type: application/octet-stream"
    ]

    # Configure the transcription parameters
    start_message = {
        "type": "Configure",
        "features": {
            "language": "en",
            "encoding": "mulaw",
            "sample_rate": 8000,
            "channels": 1,
        }
    }

    try:
        # Establish a connection to Deepgram API
        deepgram_ws = websocket.create_connection("wss://api.deepgram.com/v1/listen",
                                                  header=headers,
                                                  sslopt={"context": context})

        # Send the Configure message when the stream starts
        if audio_data.event == "start":
            deepgram_ws.send(json.dumps(start_message))
            print("Transcription initiated to Deepgram+++++++:", audio_data)

        # If the event is 'media', send the audio data (raw binary data)
        elif audio_data.event == "media":
            print("Transcription sending to Deepgram+++++++:", audio_data.media.payload)

            # Send the binary audio data (payload) directly to Deepgram
            deepgram_ws.send(audio_data.media.payload, opcode=websocket.ABNF.OPCODE_BINARY)
            print("Sent audio data to Deepgram.")

        # Receive and handle the transcription response from Deepgram
        transcription = deepgram_ws.recv()
        print("Transcription received from Deepgram+++++++:", transcription)
        if transcription:
            # Parse the transcription response from Deepgram
            try:
                data = json.loads(transcription)
                if "channel" in data and "alternatives" in data["channel"]:
                    transcript = data["channel"]["alternatives"][0].get("transcript", "")
                    print(f"Received transcript: {transcript}")
                else:
                    print("No transcript available in the message")

            except json.JSONDecodeError as e:
                print(f"Error decoding JSON: {e}")
            except Exception as e:
                print(f"Error processing message: {e}")

        else:
            print("Received empty response from Deepgram.")

        # Close the WebSocket connection
        deepgram_ws.close()

    except Exception as e:
        print(f"Error processing audio data: {e}")

# WebSocket server that listens for incoming connections
async def main():
    server = await websockets.serve(process_websocket, "localhost", 5000)
    print("Starting WebSocket server at ws://localhost:5000")
    await server.wait_closed()

if __name__ == "__main__":
    asyncio.run(main())
