# [H] Tornado: Authorization header forwarded across cross-origin redirects in SimpleAsyncHTTPClient

## Summary
Severity: High
Advisory: GHSA-3x9g-8vmp-wqvf
CVE: CVE-2026-49853
CWE: CWE-200
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2026-06-15
Source: https://github.com/advisories/GHSA-3x9g-8vmp-wqvf
Type: github-advisory

## Affected
- PyPI: `tornado` — affected >=0 <6.5.6

## Details
## Summary

When SimpleAsyncHTTPClient follows a 3xx redirect, it shallow-copies the original HTTPRequest, rewrites the URL, decrements max_redirects, and removes only the Host header. It does not clear Authorization, auth_username, auth_password, or auth_mode when the redirect target changes origin.

As a result, credentials intended for one origin can be forwarded to a different origin when follow_redirects=True, which is the default.

Beginning in Tornado 6.5.6, `SimpleAsyncHTTPClient` matches the default behavior of `libcurl` (and therefore `CurlAsyncHTTPClient`): When a redirect changes the scheme, host, or port of the url, the `Authorization` and `Cookie` headers will be removed when following the redirect.

## References
- https://github.com/tornadoweb/tornado/security/advisories/GHSA-3x9g-8vmp-wqvf
- https://github.com/tornadoweb/tornado
