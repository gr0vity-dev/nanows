import json
import asyncio
from typing import List, Union, Optional
import websockets
from websockets.exceptions import (
    ConnectionClosedError,
    WebSocketException,
    InvalidHandshake,
)


class NanoWebSocket:
    """
    A client for interacting with the Nano WebSocket server.
    """

    def __init__(self, url: str = "ws://localhost:7078"):
        """
        Initializes the NanoWebSocket client.

        Args:
            url (str): The WebSocket server URL.
        """
        self.websocket_url = url
        self.websocket: Optional[websockets.WebSocketClientProtocol] = None
        self.keepalive_task: Optional[asyncio.Task] = None

    async def connect(self):
        """
        Establishes a connection to the WebSocket server.
        """
        if self.websocket and not self.websocket.closed:
            return
        try:
            self.websocket = await websockets.connect(self.websocket_url)
            self.keepalive_task = asyncio.create_task(self._keepalive_loop())
        except (InvalidHandshake, WebSocketException) as e:
            raise ConnectionError(
                f"Failed to connect to {self.websocket_url}: {e}")

    async def disconnect(self):
        """
        Closes the WebSocket connection and cancels the keepalive task.
        """
        if self.websocket:
            await self.websocket.close()
            self.websocket = None
        if self.keepalive_task:
            self.keepalive_task.cancel()
            self.keepalive_task = None

    async def _keepalive_loop(self, interval: int = 120):
        """
        Sends keepalive messages at regular intervals.

        Args:
            interval (int): The interval in seconds between keepalive messages.
        """
        while self.websocket and not self.websocket.closed:
            try:
                await self.ping()
                await asyncio.sleep(interval)
            except (ConnectionClosedError, asyncio.CancelledError):
                break

    async def ping(self, ack: bool = False, ws_id: Optional[str] = None):
        """
        Sends a ping message to the WebSocket server.

        Args:
            ack (bool): Whether to request an acknowledgment.
            ws_id (str): An optional identifier for the message.
        """
        await self._send_message({"action": "ping"}, ack, ws_id)

    async def _send_message(
        self,
        message: dict,
        ack: bool = False,
        ws_id: Optional[str] = None,
    ):
        """
        Sends a message to the WebSocket server.

        Args:
            message (dict): The message to send.
            ack (bool): Whether to request an acknowledgment.
            ws_id (str): An optional identifier for the message.
        """
        if not self.websocket or self.websocket.closed:
            await self.connect()

        if ack:
            message["ack"] = "true"
        if ws_id:
            message["id"] = ws_id

        await self.websocket.send(json.dumps(message))

    async def subscribe(
        self,
        topic: str,
        options: Optional[dict] = None,
        ack: bool = False,
        ws_id: Optional[str] = None,
    ):
        """
        Subscribes to a topic with optional parameters.

        Args:
            topic (str): The topic to subscribe to.
            options (dict): Additional options for the subscription.
            ack (bool): Whether to request an acknowledgment.
            ws_id (str): An optional identifier for the subscription.
        """
        message = {"action": "subscribe", "topic": topic}
        if options:
            message["options"] = options
        await self._send_message(message, ack, ws_id)

    async def unsubscribe(
        self,
        topic: str,
        ack: bool = False,
        ws_id: Optional[str] = None,
    ):
        """
        Unsubscribes from a topic.

        Args:
            topic (str): The topic to unsubscribe from.
            ack (bool): Whether to request an acknowledgment.
            ws_id (str): An optional identifier for the unsubscription.
        """
        message = {"action": "unsubscribe", "topic": topic}
        await self._send_message(message, ack, ws_id)

    async def update_subscription(
        self,
        topic: str,
        accounts_add: Union[str, List[str], None] = None,
        accounts_del: Union[str, List[str], None] = None,
    ):
        """
        Updates subscription options for a given topic.

        Args:
            topic (str): The topic to update.
            accounts_add (str or list): Accounts to add.
            accounts_del (str or list): Accounts to remove.
        """
        if not self.websocket or self.websocket.closed:
            await self.connect()

        accounts_add_list = (
            [accounts_add] if isinstance(accounts_add, str) else accounts_add
        )
        accounts_del_list = (
            [accounts_del] if isinstance(accounts_del, str) else accounts_del
        )

        if accounts_add_list and accounts_del_list:
            shared_accounts = set(
                accounts_add_list).intersection(accounts_del_list)
            if shared_accounts:
                raise ValueError(
                    f"Accounts cannot be in both add and delete lists: {
                        shared_accounts}"
                )

        options = {}
        if accounts_add_list:
            options["accounts_add"] = accounts_add_list
        if accounts_del_list:
            options["accounts_del"] = accounts_del_list

        message = {"action": "update", "topic": topic, "options": options}
        await self.websocket.send(json.dumps(message))

    async def receive_messages(self, topic_filter: Optional[str] = None):
        """
        Async generator that yields messages from the WebSocket server.

        Args:
            topic_filter (str): If provided, only messages matching this topic are yielded.
        """
        while True:
            try:
                if not self.websocket or self.websocket.closed:
                    await self.connect()

                async for message in self.websocket:
                    parsed_message = json.loads(message)
                    if topic_filter:
                        if parsed_message.get("topic") == topic_filter:
                            yield parsed_message
                    else:
                        yield parsed_message

            except ConnectionClosedError:
                await self.disconnect()
                continue  # This will trigger reconnection on next iteration
            except Exception as e:
                await self.disconnect()
                raise  # Re-raise unexpected exceptions

    # Specific subscribe methods
    async def subscribe_confirmation(
        self,
        accounts: Union[str, List[str], None] = None,
        all_local_accounts: Optional[bool] = None,
        include_block: Optional[bool] = None,
        include_election_info: Optional[bool] = None,
        include_sideband_info: Optional[bool] = None,
        ack: bool = False,
        ws_id: Optional[str] = None,
    ):
        """
        Subscribes to the 'confirmation' topic with specific options.

        Args:
            accounts (str or list): Account(s) to monitor.
            all_local_accounts (bool): Monitor all local accounts.
            include_block (bool): Include block details.
            include_election_info (bool): Include election info.
            include_sideband_info (bool): Include sideband info.
            ack (bool): Whether to request an acknowledgment.
            ws_id (str): An optional identifier for the subscription.
        """
        options = {}
        if accounts:
            if isinstance(accounts, str):
                accounts = [accounts]
            options["accounts"] = accounts
        if all_local_accounts is not None:
            options["all_local_accounts"] = str(all_local_accounts).lower()
        if include_block is not None:
            options["include_block"] = str(include_block).lower()
        if include_election_info is not None:
            options["include_election_info"] = str(
                include_election_info).lower()
        if include_sideband_info is not None:
            options["include_sideband_info"] = str(
                include_sideband_info).lower()

        await self.subscribe("confirmation", options, ack, ws_id)

    async def subscribe_vote(
        self,
        representatives: Union[str, List[str], None] = None,
        include_replays: bool = False,
        include_indeterminate: bool = False,
        ack: bool = False,
        ws_id: Optional[str] = None,
    ):
        """
        Subscribes to the 'vote' topic with specific options.

        Args:
            representatives (str or list): Representatives to monitor.
            include_replays (bool): Include replay votes.
            include_indeterminate (bool): Include indeterminate votes.
            ack (bool): Whether to request an acknowledgment.
            ws_id (str): An optional identifier for the subscription.
        """
        options = {
            "include_replays": str(include_replays).lower(),
            "include_indeterminate": str(include_indeterminate).lower(),
        }
        if representatives:
            if isinstance(representatives, str):
                representatives = [representatives]
            options["representatives"] = representatives

        await self.subscribe("vote", options, ack, ws_id)

    async def subscribe_telemetry(
        self, ack: bool = False, ws_id: Optional[str] = None
    ):
        await self.subscribe("telemetry", ack=ack, ws_id=ws_id)

    async def subscribe_started_election(
        self, ack: bool = False, ws_id: Optional[str] = None
    ):
        await self.subscribe("started_election", ack=ack, ws_id=ws_id)

    async def subscribe_stopped_election(
        self, ack: bool = False, ws_id: Optional[str] = None
    ):
        await self.subscribe("stopped_election", ack=ack, ws_id=ws_id)

    async def subscribe_new_unconfirmed_block(
        self, ack: bool = False, ws_id: Optional[str] = None
    ):
        await self.subscribe("new_unconfirmed_block", ack=ack, ws_id=ws_id)

    async def subscribe_bootstrap(
        self, ack: bool = False, ws_id: Optional[str] = None
    ):
        await self.subscribe("bootstrap", ack=ack, ws_id=ws_id)

    async def subscribe_active_difficulty(
        self, ack: bool = False, ws_id: Optional[str] = None
    ):
        await self.subscribe("active_difficulty", ack=ack, ws_id=ws_id)

    async def subscribe_work(
        self, ack: bool = False, ws_id: Optional[str] = None
    ):
        await self.subscribe("work", ack=ack, ws_id=ws_id)

    # Specific unsubscribe methods
    async def unsubscribe_confirmation(
        self, ack: bool = False, ws_id: Optional[str] = None
    ):
        await self.unsubscribe("confirmation", ack, ws_id)

    async def unsubscribe_vote(
        self, ack: bool = False, ws_id: Optional[str] = None
    ):
        await self.unsubscribe("vote", ack, ws_id)

    async def unsubscribe_telemetry(
        self, ack: bool = False, ws_id: Optional[str] = None
    ):
        await self.unsubscribe("telemetry", ack, ws_id)

    async def unsubscribe_started_election(
        self, ack: bool = False, ws_id: Optional[str] = None
    ):
        await self.unsubscribe("started_election", ack, ws_id)

    async def unsubscribe_stopped_election(
        self, ack: bool = False, ws_id: Optional[str] = None
    ):
        await self.unsubscribe("stopped_election", ack, ws_id)

    async def unsubscribe_new_unconfirmed_block(
        self, ack: bool = False, ws_id: Optional[str] = None
    ):
        await self.unsubscribe("new_unconfirmed_block", ack, ws_id)

    async def unsubscribe_bootstrap(
        self, ack: bool = False, ws_id: Optional[str] = None
    ):
        await self.unsubscribe("bootstrap", ack, ws_id)

    async def unsubscribe_active_difficulty(
        self, ack: bool = False, ws_id: Optional[str] = None
    ):
        await self.unsubscribe("active_difficulty", ack, ws_id)

    async def unsubscribe_work(
        self, ack: bool = False, ws_id: Optional[str] = None
    ):
        await self.unsubscribe("work", ack, ws_id)
