import json
import websockets
from typing import List, Union
from asyncio import create_task, sleep


class NanoWebSocket:
    def __init__(self, url: str = "ws://localhost:7078"):
        self.websocket_url = url
        self.websocket = None
        self.keepalive_task = None

    async def connect(self):
        self.websocket = await websockets.connect(self.websocket_url)
        self.keepalive_task = create_task(self.bg_keepalive())

    async def disconnect(self):
        if self.websocket:
            await self.websocket.close()
            self.websocket = None
        if self.keepalive_task:
            self.keepalive_task.cancel()
            self.keepalive_task = None

    async def bg_keepalive(self, interval=120):
        while self.websocket and not self.websocket.closed:
            await self.keepalive()
            await sleep(interval)

    async def keepalive(self):
        if not self.websocket:
            await self.connect()

        subscribe_message = {
            "action": "ping"
        }

        await self.websocket.send(json.dumps(subscribe_message))

    async def subscribe(self, topic: str, options: dict = None):
        if not self.websocket:
            await self.connect()

        subscribe_message = {
            "action": "subscribe",
            "topic": topic,
            "options": options or {}
        }

        await self.websocket.send(json.dumps(subscribe_message))

    async def unsubscribe(self, topic: str):
        if not self.websocket:
            raise ConnectionError()

        unsubscribe_message = {
            "action": "unsubscribe",
            "topic": topic
        }

        await self.websocket.send(json.dumps(unsubscribe_message))

    async def subscribe_confirmation(self, accounts: Union[str, List[str]] = None, all_local_accounts=None):
        if isinstance(accounts, str):
            accounts = [accounts]

        options = {}
        if accounts:
            options["accounts"] = accounts
        if all_local_accounts:
            options["all_local_accounts"] = str(all_local_accounts).lower()

        await self.subscribe("confirmation", options)

    async def unsubscribe_confirmation(self):
        await self.unsubscribe("confirmation")

    async def subscribe_vote(self, representatives: List[str] = None, include_replays=False, include_indeterminate=False):
        options = {
            "include_replays": str(include_replays).lower(),
            "include_indeterminate": str(include_indeterminate).lower(),
        }
        if representatives:
            options["representatives"] = representatives

        await self.subscribe("vote", options)

    async def unsubscribe_vote(self):
        await self.unsubscribe("vote")

    async def subscribe_telemetry(self):
        await self.subscribe("telemetry")

    async def unsubscribe_telemetry(self):
        await self.unsubscribe("telemetry")

    async def subscribe_started_election(self):
        await self.subscribe("started_election")

    async def unsubscribe_started_election(self):
        await self.unsubscribe("started_election")

    async def subscribe_stopped_election(self):
        await self.subscribe("stopped_election")

    async def unsubscribe_stopped_election(self):
        await self.unsubscribe("stopped_election")

    async def subscribe_new_unconfirmed_block(self):
        await self.subscribe("new_unconfirmed_block")

    async def unsubscribe_new_unconfirmed_block(self):
        await self.unsubscribe("new_unconfirmed_block")

    async def subscribe_bootstrap(self):
        await self.subscribe("bootstrap")

    async def unsubscribe_bootstrap(self):
        await self.unsubscribe("bootstrap")

    async def subscribe_active_difficulty(self):
        await self.subscribe("active_difficulty")

    async def unsubscribe_active_difficulty(self):
        await self.unsubscribe("active_difficulty")

    async def subscribe_work(self):
        await self.subscribe("work")

    async def unsubscribe_work(self):
        await self.unsubscribe("work")

    async def update_subscription(self, topic: str, accounts_add: Union[str, List[str]] = None, accounts_del: Union[str, List[str]] = None):
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
            "topic": topic,
            "options": {}
        }

        if accounts_add:
            update_message["options"]["accounts_add"] = accounts_add

        if accounts_del:
            update_message["options"]["accounts_del"] = accounts_del

        await self.websocket.send(json.dumps(update_message))

    async def receive_messages(self, topic=None):
        if not self.websocket:
            raise RuntimeError("Not connected to WebSocket")

        async for message in self.websocket:
            parsed_message = json.loads(message)
            if topic:
                if "topic" in parsed_message and parsed_message["topic"] == topic:
                    yield parsed_message
            else:
                yield parsed_message
