import asyncio
from nanows.api import NanoWebSocket


async def run():
    accounts = [
        "nano_1a...", "nano_1b..."]
    nano_ws = NanoWebSocket(url="ws://localhost:7078")

    await nano_ws.subscribe_confirmation(accounts)
    async for confirmation in nano_ws.get_confirmations():
        print(f"Received confirmation: {confirmation}")

asyncio.run(run())
