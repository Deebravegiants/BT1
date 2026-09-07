# [M] Gakido vulnerable to HTTP Header Injection (CRLF Injection) 

## Summary
Severity: Medium
Advisory: GHSA-gcgx-chcp-hxp9
CVE: CVE-2026-24489
CWE: CWE-113, CWE-93
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2026-01-26
Source: https://github.com/advisories/GHSA-gcgx-chcp-hxp9
Type: github-advisory

## Affected
- PyPI: `gakido` — affected >=0 <0.1.1

## Details
A vulnerability was discovered in Gakido that allowed HTTP Header Injection through CRLF (Carriage Return Line Feed) sequences in user-supplied header values and names.

When making HTTP requests with user-controlled header values containing `\r\n` (CRLF), `\n` (LF), or `\x00` (null byte) characters, an attacker could inject arbitrary HTTP headers into the request.

## Impact

An attacker who can control header values passed to Gakido's `Client.get()`, `Client.post()`, or other request methods could:

1. **Inject arbitrary HTTP headers** - Add malicious headers to requests
2. **HTTP Response Splitting** - Potentially manipulate responses in certain proxy configurations
3. **Cache Poisoning** - Inject headers that could poison intermediate caches
4. **Session Fixation** - Inject session-related headers
5. **Bypass Security Controls** - Inject headers that bypass server-side security checks

## Proof of Concept

```python
from gakido import Client

# Before fix: X-Injected header would be sent as a separate header
c = Client(impersonate="chrome_120")
r = c.get("https://httpbin.org/headers", headers={
    "User-Agent": "test\r\nX-Injected: pwned"
})

# The server would receive:
# User-Agent: test
# X-Injected: pwned
```

## Affected Code

The vulnerability existed in the header processing logic where user-supplied headers were not sanitized before being sent in HTTP requests.

**File:** `gakido/headers.py`  
**Function:** `canonicalize_headers()`

## Fix

The fix adds a `_sanitize_header()` function that strips `\r`, `\n`, and `\x00` characters from both header names and values before they are included in HTTP requests.

```python
def _sanitize_header(name: str, value: str) -> tuple[str, str]:
    """
    Sanitize header name and value to prevent HTTP header injection (CRLF injection).
    Strips CR, LF, and null bytes from both name and value.
    """
    clean_name = name.replace("\r", "").replace("\n", "").replace("\x00", "")
    clean_value = value.replace("\r", "").replace("\n", "").replace("\x00", "")
    return clean_name, clean_value
```

## References
- https://github.com/HappyHackingSpace/gakido/security/advisories/GHSA-gcgx-chcp-hxp9
- https://nvd.nist.gov/vuln/detail/CVE-2026-24489
- https://github.com/HappyHackingSpace/gakido/commit/369c67e67c63da510c8a9ab021e54a92ccf1f788
- https://github.com/HappyHackingSpace/gakido
- https://github.com/HappyHackingSpace/gakido/releases/tag/v0.1.1-1bc6019
