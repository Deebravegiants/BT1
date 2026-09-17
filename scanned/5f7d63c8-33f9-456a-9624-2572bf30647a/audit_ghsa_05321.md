# [M] PraisonAI: Unauthenticated Event Injection via SSE `/publish` Endpoint

## Summary
Severity: Medium
Advisory: GHSA-35w5-pcw4-jx94
CVE: CVE-2026-57128
CWE: CWE-306
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2026-06-18
Source: https://github.com/advisories/GHSA-35w5-pcw4-jx94
Type: github-advisory

## Affected
- PyPI: `praisonaiagents` — affected >=0 <1.6.59

## Details
## Summary

The SSE (Server-Sent Events) server in `src/praisonai-agents/praisonaiagents/server/server.py` exposes a `/publish` endpoint that broadcasts arbitrary messages to all connected clients without any authentication. The `ServerConfig` dataclass (line 24) defines an `auth_token` field, but this token is never validated in the `/publish` or `/events` request handlers. Any attacker with access to the SSE server port can inject arbitrary events into the SSE stream visible to all connected clients, or use `/info` to leak server configuration including connected client count.

## Details

**Vulnerable code (lines 164–180):**
```python
async def publish(request):
    try:
        data = await request.json()
        event_type = data.get("type", "message")
        event_data = data.get("data", {})

        self.broadcast(event_type, event_data)

        return JSONResponse({
            "success": True,
            "clients": len(self._clients),
        })
```

The `auth_token` field in `ServerConfig` (line 31):
```python
@dataclass
class ServerConfig:
    ...
    auth_token: Optional[str] = None
```

This `auth_token` is **never referenced** in any request handler. The `/publish` endpoint processes any POST request regardless of authentication headers. The `/info` endpoint (line 182) also has no auth and returns server configuration including `self.config.to_dict()`.

**Routes registration (lines 190–194):**
```python
routes = [
    Route("/health", health, methods=["GET"]),
    Route("/events", events, methods=["GET"]),
    Route("/publish", publish, methods=["POST"]),
    Route("/info", info, methods=["GET"]),
]
```

No authentication middleware or token validation is applied to any route.

## PoC

**Setup:** Start the SSE server (default port 8765). This is the documented server mode for streaming agent events.

**Positive trigger — unauthenticated event injection:**
```bash
# From any network-reachable host:
curl -X POST http://localhost:8765/publish \
  -H "Content-Type: application/json" \
  -d '{"type": "message", "data": {"text": "INJECTED: arbitrary content sent to all clients"}}'
```

**Expected response:**
```json
{"success": true, "clients": 3}
```

The response confirms the injection was broadcast to all connected SSE clients, and leaks the number of connected clients.

**Positive trigger — info leak:**
```bash
curl http://localhost:8765/info
```

**Expected response:**
```json
{
  "name": "PraisonAI Agent Server",
  "version": "1.0.0",
  "clients": 3,
  "config": {
    "host": "127.0.0.1",
    "port": 8765,
    "auth_token": "***",
    ...
  }
}
```

**Negative control — if auth were enforced:**
A request without a valid `Authorization: Bearer <token>` header should return 401 Unauthorized. Currently, it returns 200 OK with no auth check.

**Cleanup:** No persistent changes.

## Impact

An attacker with access to the SSE server port (default 8765, bound to `127.0.0.1` by default per `DEFAULT_HOST` at line 21) can:

- **Inject arbitrary events** into the SSE stream, potentially causing connected client applications to process malicious data, trigger actions, or display misleading content
- **Leak server configuration** including number of connected clients and server settings via `/info`
- **Use the response** to confirm connected client count, enabling reconnaissance

While the default binds to localhost, deployments in containers or cloud environments commonly override the host to `0.0.0.0` to allow external access. When the host is overridden, this is exploitable from the network without authentication.

## Suggested remediation

1. **Validate `auth_token`** in the `/publish` and `/events` handlers:
```python
async def publish(request):
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    if self.config.auth_token and token != self.config.auth_token:
        return JSONResponse({"error": "Unauthorized"}, status_code=401)
    # ... proceed with broadcast
```

2. Apply the same token validation to `/events` (for reading) and `/info`.

3. The default binding to `127.0.0.1` is appropriate; maintain this default and warn when overridden to `0.0.0.0`.

4. Document the `auth_token` configuration option and recommend setting it in production.

## References
- https://github.com/MervinPraison/PraisonAI/security/advisories/GHSA-35w5-pcw4-jx94
- https://github.com/MervinPraison/PraisonAI
