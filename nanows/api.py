import json
from typing import List, Union
from asyncio import create_task, sleep
import websockets


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

    async def keepalive(self, ack=False, ws_id=None):
        if not self.websocket:
            await self.connect()

        ws_message = {
            "action": "ping"
        }
        self.extend_ack_id(ws_message, ack, ws_id)

        await self.websocket.send(json.dumps(ws_message))

    def extend_ack_id(self, msg, ack, ws_id):
        msg["ack"] = str(ack).lower()
        if ws_id:
            msg["id"] = ws_id

    async def subscribe(self, topic: str, options: dict = None, ack=False, ws_id=None):
        if not self.websocket:
            await self.connect()

        ws_message = {
            "action": "subscribe",
            "topic": topic,
            "options": options or {}
        }
        self.extend_ack_id(ws_message, ack, ws_id)

        await self.websocket.send(json.dumps(ws_message))

    async def subscribe_confirmation(self,
                                     accounts: Union[str, List[str]] = None,
                                     all_local_accounts=None,
                                     include_block=None,
                                     include_sideband_info=None,
                                     include_election_info=None,
                                     ack=False, ws_id=None):
        if isinstance(accounts, str):
            accounts = [accounts]

        options = {}
        if accounts:
            options["accounts"] = accounts
        if all_local_accounts:
            options["all_local_accounts"] = str(all_local_accounts).lower()
        if include_block:
            options["include_block"] = str(include_block).lower()
        if include_sideband_info:
            options["include_sideband_info"] = str(
                include_sideband_info).lower()
        if include_election_info:
            options["include_election_info"] = str(
                include_election_info).lower()

        await self.subscribe("confirmation", options, ack, ws_id)

    async def subscribe_vote(self,
                             representatives: List[str] = None,
                             include_replays=False,
                             include_indeterminate=False,
                             ack=False, ws_id=None):
        options = {
            "include_replays": str(include_replays).lower(),
            "include_indeterminate": str(include_indeterminate).lower(),
        }
        if representatives:
            options["representatives"] = representatives

        await self.subscribe("vote", options, ack, ws_id)

    async def subscribe_telemetry(self, ack=False, ws_id=None):
        await self.subscribe("telemetry", ack=ack, ws_id=ws_id)

    async def subscribe_started_election(self, ack=False, ws_id=None):
        await self.subscribe("started_election", ack=ack, ws_id=ws_id)

    async def subscribe_stopped_election(self, ack=False, ws_id=None):
        await self.subscribe("stopped_election", ack=ack, ws_id=ws_id)

    async def subscribe_new_unconfirmed_block(self, ack=False, ws_id=None):
        await self.subscribe("new_unconfirmed_block", ack=ack, ws_id=ws_id)

    async def subscribe_bootstrap(self, ack=False, ws_id=None):
        await self.subscribe("bootstrap", ack=ack, ws_id=ws_id)

    async def subscribe_active_difficulty(self, ack=False, ws_id=None):
        await self.subscribe("active_difficulty", ack=ack, ws_id=ws_id)

    async def subscribe_work(self, ack=False, ws_id=None):
        await self.subscribe("work", ack=ack, ws_id=ws_id)

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

    async def unsubscribe_work(self, ack=False, ws_id=None):
        await self.unsubscribe("work", ack=ack, ws_id=ws_id)

    async def unsubscribe(self, topic: str, ack=False, ws_id=None):
        if not self.websocket:
            raise ConnectionError()

        ws_message = {
            "action": "unsubscribe",
            "topic": topic
        }
        self.extend_ack_id(ws_message, ack, ws_id)

        await self.websocket.send(json.dumps(ws_message))

    async def unsubscribe_confirmation(self, ack=False, ws_id=None):
        await self.unsubscribe("confirmation", ack=ack, ws_id=ws_id)

    async def unsubscribe_vote(self, ack=False, ws_id=None):
        await self.unsubscribe("vote", ack=ack, ws_id=ws_id)

    async def unsubscribe_telemetry(self, ack=False, ws_id=None):
        await self.unsubscribe("telemetry", ack=ack, ws_id=ws_id)

    async def unsubscribe_started_election(self, ack=False, ws_id=None):
        await self.unsubscribe("started_election", ack=ack, ws_id=ws_id)

    async def unsubscribe_stopped_election(self, ack=False, ws_id=None):
        await self.unsubscribe("stopped_election", ack=ack, ws_id=ws_id)

    async def unsubscribe_new_unconfirmed_block(self, ack=False, ws_id=None):
        await self.unsubscribe("new_unconfirmed_block", ack=ack, ws_id=ws_id)

    async def unsubscribe_bootstrap(self, ack=False, ws_id=None):
        await self.unsubscribe("bootstrap", ack=ack, ws_id=ws_id)

    async def unsubscribe_active_difficulty(self, ack=False, ws_id=None):
        await self.unsubscribe("active_difficulty", ack=ack, ws_id=ws_id)

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
