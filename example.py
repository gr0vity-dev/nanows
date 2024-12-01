import asyncio
from nanows.api import NanoWebSocket


async def run_forever():
    """
    Runs a WebSocket connection that automatically reconnects on failures.
    Continues running indefinitely until interrupted by the user.
    """
    nano_ws = NanoWebSocket(url="ws://localhost:7078")
    retry_delay = 5  # seconds

    while True:
        try:
            await nano_ws.connect()

            # Subscribe to desired topics
            await nano_ws.subscribe_telemetry()
            await nano_ws.subscribe_confirmation()

            print("Connected and subscribed successfully!")

            async for message in nano_ws.receive_messages():
                print(f"Received message: {message}")

        except KeyboardInterrupt:
            print("Interrupted by user.")
            break

        except Exception as e:
            print(f"Connection error: {e}")
            print(f"Retrying in {retry_delay} seconds...")
            await asyncio.sleep(retry_delay)
            continue

        finally:
            await nano_ws.disconnect()

# Run the example
if __name__ == "__main__":
    asyncio.run(run_forever())
