import websockets
import json
from typing import Union, List


class NanoWebSocket:
    def __init__(self, url: str = "ws://localhost:7078"):
        self.websocket_url = url
        self.websocket = None

    async def connect(self):
        self.websocket = await websockets.connect(self.websocket_url)

    async def subscribe_confirmation(self, accounts: Union[str, List[str]]):
        if not self.websocket:
            await self.connect()

        # Check if accounts is a string and convert to a list if needed
        if isinstance(accounts, str):
            accounts = [accounts]

        # Subscribe to the accounts
        await self.websocket.send(json.dumps({
            "action": "subscribe",
            "topic": "confirmation",
            "options": {
                "all_local_accounts": False,
                "accounts": accounts
            }
        }))

    async def update_confirmation(self,
                                  accounts_add: Union[str, List[str]] = None,
                                  accounts_del: Union[str, List[str]] = None):
        if not self.websocket:
            await self.connect()

        if isinstance(accounts_add, str):
            accounts_add = [accounts_add]

        if isinstance(accounts_del, str):
            accounts_del = [accounts_del]

        if accounts_add and accounts_del:
            shared_accounts = set(accounts_add).intersection(accounts_del)
            if shared_accounts:
                raise ValueError(
                    f"Shared accounts found in both add and delete lists: {shared_accounts}")

        update_message = {
            "action": "update",
            "topic": "confirmation",
            "options": {}
        }

        if accounts_add:
            update_message["options"]["accounts_add"] = accounts_add

        if accounts_del:
            update_message["options"]["accounts_del"] = accounts_del

        await self.websocket.send(json.dumps(update_message))

    async def get_confirmations(self):
        if not self.websocket:
            raise RuntimeError("Not connected to WebSocket")

        async for message in self.websocket:
            yield json.loads(message)
