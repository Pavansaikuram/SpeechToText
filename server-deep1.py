import asyncio
import websockets
import json
import ssl


async def send_to_deepgram(audio_bytes):
    """Sends audio data to Deepgram WebSocket API and returns the transcription."""
    deepgram_ws_url = "wss://api.deepgram.com/v1/listen"

    headers = {
        "Authorization": "Token APIKEY",  # Replace with your Deepgram API token
        "Content-Type": "application/octet-stream"
    }

    context = ssl.create_default_context()

    try:
        async with websockets.connect(deepgram_ws_url, additional_headers=headers, ssl=context) as dg_ws:
            # Send Deepgram configuration message
            config_message = {
                "type": "Configure",
                "features": {
                    "language": "en",
                    "encoding": "linear16",
                    "sample_rate": 16000
                }
            }
            await dg_ws.send(json.dumps(config_message))

            # Send audio data
            await dg_ws.send(audio_bytes)

            # Receive and parse the transcription response
            async for response in dg_ws:
                data = json.loads(response)
                if "channel" in data and "alternatives" in data["channel"]:
                    transcript = data["channel"]["alternatives"][0].get("transcript", "")
                    return transcript
                else:
                    return "No transcript available"

    except Exception as e:
        return f"Error with Deepgram: {e}"


# WebSocket server function
async def process_websocket(websocket):
    """Handles incoming audio messages from clients."""
    async for message in websocket:
        print("Received audio data")

        # Send audio to Deepgram and get transcription
        text = await send_to_deepgram(message)

        # Send transcription back to client
        await websocket.send(text)


async def main():
    """Starts the WebSocket server."""
    server = await websockets.serve(process_websocket, "localhost", 5000)
    print("Starting WebSocket server at ws://localhost:5000")
    await server.wait_closed()


if __name__ == "__main__":
    asyncio.run(main())
