import pytest
import asyncio
from unittest.mock import Mock, patch
from websockets.exceptions import ConnectionClosedError
from nanows.api import NanoWebSocket


@pytest.mark.asyncio
async def test_connection_restoration():
    """Test that the connection is automatically restored after being dropped."""

    # Mock websockets.connect to track connection attempts
    connect_count = 0

    class MockWebSocket:
        def __init__(self):
            nonlocal connect_count
            connect_count += 1
            self.closed = False
            if connect_count == 1:
                self.messages = ['{"topic": "telemetry", "message": "first"}']
            else:
                self.messages = [
                    '{"topic": "telemetry", "message": "after_reconnect"}']
            self.message_index = 0

        async def send(self, message):
            pass

        async def close(self):
            self.closed = True

        def __aiter__(self):
            return self

        async def __anext__(self):
            # Simulate connection drop after first message
            if self.message_index == 1:
                raise ConnectionClosedError(None, None)

            if self.message_index >= len(self.messages):
                raise StopAsyncIteration

            message = self.messages[self.message_index]
            self.message_index += 1
            return message

    async def mock_connect(*args, **kwargs):
        return MockWebSocket()

    # Patch websockets.connect with our mock
    with patch('websockets.connect', mock_connect):
        nano_ws = NanoWebSocket(url="ws://test")
        received_messages = []
        run_loop = True
        while run_loop:
            try:
                await nano_ws.connect()
                await nano_ws.subscribe_telemetry()

                # Try to receive messages, including after connection drop
                async for message in nano_ws.receive_messages():
                    received_messages.append(message)
                    if len(received_messages) >= 2:  # Stop after getting both messages
                        run_loop = False

            except Exception as e:
                pass

            finally:
                await nano_ws.disconnect()

    # Verify that we connected more than once (indicating reconnection)
    assert connect_count == 2, "Connection was not retried after drop"
    # Add this line for debugging
    print("Received messages:", received_messages)

    # Verify we got messages before and after the reconnection
    assert len(
        received_messages) == 2, "Did not receive expected number of messages"
    assert received_messages[0]["message"] == "first"
    assert received_messages[1]["message"] == "after_reconnect"
