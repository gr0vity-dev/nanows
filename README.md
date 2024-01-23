# nanows

`nanows` is a Python library providing an easy-to-use interface for interacting with Nano cryptocurrency nodes via WebSockets. It abstracts the complexities of WebSocket communication, allowing developers to focus on handling Nano node events like account confirmations.

## Features

- Subscribe to confirmation events for specific Nano accounts.
- Update subscription settings to add or remove accounts dynamically.
- Stream confirmation events in real-time with an asynchronous API.

## Installation

To install `nanows`, run:

```bash
pip install nanows
```

## Quick Start

Here's a quick example to get you started:

```python
import asyncio
from nanows.api import NanoWebSocket

async def run():
    accounts = ["nano_1a...", "nano_1b..."]
    nano_ws = NanoWebSocket(url="ws://localhost:7078")

    await nano_ws.subscribe_confirmation(accounts)
    async for confirmation in nano_ws.get_confirmations():
        print(f"Received confirmation: {confirmation}")

asyncio.run(run())
```

This example demonstrates how to subscribe to confirmation events for a list of Nano accounts and print out each confirmation as it is received.


## Contributing

Contributions to `nanows` are welcome! 

## License

`nanows` is released under the MIT License.