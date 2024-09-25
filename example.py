import asyncio
from nanows.api import NanoWebSocket


async def run():
    nano_ws = NanoWebSocket(url="ws://localhost:7078")
    await nano_ws.connect()

    await nano_ws.subscribe_telemetry()
    await nano_ws.subscribe_confirmation()

    try:
        async for message in nano_ws.receive_messages():
            print(f"Received message: {message}")
    except KeyboardInterrupt:
        print("Interrupted by user.")
    finally:
        await nano_ws.disconnect()


asyncio.run(run())
