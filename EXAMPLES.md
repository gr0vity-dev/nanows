# Nano WebSocket API Examples

This document provides examples for using the Nano WebSocket API client.

## Basic Setup

```python
import asyncio
from nanows.api import NanoWebSocket

async def main():
    # Initialize client (defaults to ws://localhost:7078)
    ws =  NanoWebSocket(url="ws://localhost:7078")
    
    # Connect to the WebSocket server
    await ws.connect()
    
    # ... use the client ...
    
    # Disconnect when done
    await ws.disconnect()

asyncio.run(main())
```

## Confirmation Monitoring

### Monitor All Confirmations
```python
async def monitor_all_confirmations():
    ws =  NanoWebSocket(url="ws://localhost:7078")
    await ws.connect()
    
    # Subscribe to all confirmations
    await ws.subscribe_confirmation()
    
    # Process incoming messages
    async for message in ws.receive_messages("confirmation"):
        print(f"New confirmation: {message}")
```

### Monitor Specific Accounts
```python
async def monitor_specific_accounts():
    ws =  NanoWebSocket(url="ws://localhost:7078")
    await ws.connect()
    
    accounts = [
        "nano_16c4ush661bbn2hxc6iqrunwoyqt95in4hmw6uw7tk37yfyi77s7dyxaw8ce",
        "nano_3dmtrrws3pocycmbqwawk6xs7446qxa36fcncush4s1pejk16ksbmakis32c"
    ]
    
    await ws.subscribe_confirmation(
        accounts=accounts,
        include_election_info=True,
        include_block=True
    )
    
    async for message in ws.receive_messages("confirmation"):
        print(f"Account confirmation: {message}")
```

## Vote Monitoring

### Monitor Representative Votes
```python
async def monitor_votes():
    ws =  NanoWebSocket(url="ws://localhost:7078")
    await ws.connect()
    
    representatives = [
        "nano_3msc38fyn67pgio16dj586pdrceahtn75qgnx7fy19wscixrc8dbb3abhbw6"
    ]
    
    await ws.subscribe_vote(
        representatives=representatives,
        include_replays=True,
        include_indeterminate=False
    )
    
    async for message in ws.receive_messages("vote"):
        print(f"Vote received: {message}")
```

## Network Difficulty Monitoring

```python
async def monitor_network_difficulty():
    ws =  NanoWebSocket(url="ws://localhost:7078")
    await ws.connect()
    
    await ws.subscribe_active_difficulty()
    
    async for message in ws.receive_messages("active_difficulty"):
        print(f"Network difficulty update: {message}")
```

## Block Processing Monitoring

### Monitor New Unconfirmed Blocks
```python
async def monitor_new_blocks():
    ws =  NanoWebSocket(url="ws://localhost:7078")
    await ws.connect()
    
    await ws.subscribe_new_unconfirmed_block()
    
    async for message in ws.receive_messages("new_unconfirmed_block"):
        print(f"New unconfirmed block: {message}")
```

### Monitor Election Events
```python
async def monitor_elections():
    ws =  NanoWebSocket(url="ws://localhost:7078")
    await ws.connect()
    
    # Subscribe to both started and stopped elections
    await ws.subscribe_started_election()
    await ws.subscribe_stopped_election()
    
    async for message in ws.receive_messages():
        if message["topic"] == "started_election":
            print(f"Election started: {message}")
        elif message["topic"] == "stopped_election":
            print(f"Election stopped: {message}")
```

## Node Telemetry Monitoring

```python
async def monitor_telemetry():
    ws =  NanoWebSocket(url="ws://localhost:7078")
    await ws.connect()
    
    await ws.subscribe_telemetry()
    
    async for message in ws.receive_messages("telemetry"):
        print(f"Telemetry update: {message}")
```

## Work Generation Monitoring

```python
async def monitor_work_generation():
    ws =  NanoWebSocket(url="ws://localhost:7078")
    await ws.connect()
    
    await ws.subscribe_work()
    
    async for message in ws.receive_messages("work"):
        print(f"Work generation event: {message}")
```

## Bootstrap Process Monitoring

```python
async def monitor_bootstrap():
    ws =  NanoWebSocket(url="ws://localhost:7078")
    await ws.connect()
    
    await ws.subscribe_bootstrap()
    
    async for message in ws.receive_messages("bootstrap"):
        print(f"Bootstrap event: {message}")
```

## Updating Subscriptions

```python
async def update_confirmation_subscription():
    ws =  NanoWebSocket(url="ws://localhost:7078")
    await ws.connect()
    
    # Initial subscription
    await ws.subscribe_confirmation(accounts=["account1", "account2"])
    
    # Later, add/remove accounts
    await ws.update_subscription(
        topic="confirmation",
        accounts_add=["account3", "account4"],
        accounts_del=["account1"]
    )
```

## Error Handling

```python
async def handle_websocket_errors():
    ws =  NanoWebSocket(url="ws://localhost:7078")
    
    try:
        await ws.connect()
        await ws.subscribe_confirmation()
        
        async for message in ws.receive_messages("confirmation"):
            try:
                # Process message
                print(message)
            except Exception as e:
                print(f"Error processing message: {e}")
                
    except ConnectionError as e:
        print(f"Connection error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
    finally:
        await ws.disconnect()
```