# NanoWS Documentation

## Overview
NanoWS is a Python library for interacting with Nano cryptocurrency nodes via WebSocket connections. It provides an asynchronous interface for subscribing to and receiving various types of node events.

## Quick Start

```python
import asyncio
from nanows.api import NanoWebSocket

async def run_forever():
    nano_ws = NanoWebSocket(url="ws://localhost:7078")
    
    while True:
        try:
            await nano_ws.connect()
            await nano_ws.subscribe_telemetry()
            
            async for message in nano_ws.receive_messages():
                print(f"Received: {message}")
                
        except Exception as e:
            print(f"Connection error: {e}")
            await asyncio.sleep(5)  # Retry delay
            continue
            
        finally:
            await nano_ws.disconnect()

asyncio.run(run_forever())
```

## Core Features

### Connection Management
```python
ws = NanoWebSocket(url="ws://localhost:7078")
await ws.connect()    # Connect to node
await ws.disconnect() # Close connection
```

### Automatic Reconnection
The library automatically handles connection drops and reconnects. All subscriptions are restored after reconnection.

## Subscription Topics

### 1. Confirmation Events
Track confirmed blocks in real-time:

```python
await ws.subscribe_confirmation(
    accounts=["nano_account1", "nano_account2"],  # Optional: specific accounts
    include_block=True,                           # Include block contents
    include_election_info=True,                   # Include voting details
    include_sideband_info=True                    # Include block height & timestamp
)
```

Sample confirmation message:
```json
{
    "topic": "confirmation",
    "message": {
        "account": "nano_1...",
        "amount": "1000000000000000000000000",
        "hash": "...",
        "confirmation_type": "active_quorum",
        "block": {
            "type": "state",
            "account": "nano_1...",
            "previous": "...",
            "representative": "nano_3...",
            "balance": "1000000000",
            "link": "...",
            "signature": "...",
            "work": "...",
            "subtype": "send"
        }
    }
}
```

### 2. Telemetry Updates
Monitor node statistics:

```python
await ws.subscribe_telemetry()
```

Sample telemetry message:
```json
{
    "topic": "telemetry",
    "message": {
        "block_count": "51571901",
        "cemented_count": "51571901", 
        "unchecked_count": "0",
        "account_count": "1376750",
        "bandwidth_cap": "10485760",
        "peer_count": "261",
        "protocol_version": "18",
        "uptime": "1223618",
        "major_version": "21",
        "timestamp": "1594654710521"
    }
}
```

### 3. Vote Tracking
Monitor network votes:

```python
await ws.subscribe_vote(
    representatives=["nano_rep1", "nano_rep2"],  # Optional: specific representatives
    include_replays=False,                       # Include repeated votes
    include_indeterminate=False                  # Include votes without elections
)
```

Sample vote message:
```json
{
    "topic": "vote",
    "message": {
        "account": "nano_1...",
        "signature": "...",
        "sequence": "855471574",
        "blocks": ["..."],
        "type": "vote"  # Can be: vote, replay, indeterminate
    }
}
```

## Best Practices

1. **Error Handling**: Always implement retry logic with delays
```python
try:
    await ws.connect()
except Exception as e:
    print(f"Connection failed: {e}")
    await asyncio.sleep(5)  # Wait before retry
```

2. **Message Filtering**: Use topic filters to reduce processing overhead
```python
async for msg in ws.receive_messages(topic_filter="confirmation"):
    process_confirmation(msg)
```

3. **Resource Management**: Always close connections properly
```python
try:
    await ws.connect()
    # ... work with connection
finally:
    await ws.disconnect()
```

4. **Subscription Management**: Group related subscriptions
```python
# Monitor account activity
await ws.subscribe_confirmation(accounts=["account1"])
await ws.subscribe_vote(representatives=["account1"])
```

## Common Use Cases

### 1. Transaction Monitoring
```python
async def monitor_transactions():
    ws = NanoWebSocket()
    await ws.connect()
    await ws.subscribe_confirmation(
        accounts=["nano_account"],
        include_block=True
    )
    
    async for msg in ws.receive_messages("confirmation"):
        if msg["block"]["subtype"] == "send":
            process_send(msg)
```

### 2. Network Statistics
```python
async def track_network_stats():
    ws = NanoWebSocket()
    await ws.connect()
    await ws.subscribe_telemetry()
    
    async for msg in ws.receive_messages("telemetry"):
        update_stats(msg["message"])
```

### 3. Representative Monitoring
```python
async def monitor_representative():
    ws = NanoWebSocket()
    await ws.connect()
    await ws.subscribe_vote(
        representatives=["nano_rep1"]
    )
    
    async for msg in ws.receive_messages("vote"):
        track_voting_activity(msg)