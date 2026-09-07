# [H] urllib3: Sensitive headers forwarded across origins in proxied low-level redirects

## Summary
Severity: High
Advisory: GHSA-qccp-gfcp-xxvc
CVE: CVE-2026-44431
CWE: CWE-200
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-05-11
Source: https://github.com/advisories/GHSA-qccp-gfcp-xxvc
Type: github-advisory

## Affected
- PyPI: `urllib3` — affected >=1.23 <2.7.0

## Details
### Impact

When following cross-origin redirects for requests made using urllib3’s high-level APIs, such as `urllib3.request()`, `PoolManager.request()`, and `ProxyManager.request()`, sensitive headers — `Authorization`, `Cookie`, and `Proxy-Authorization` (defined in `Retry.DEFAULT_REMOVE_HEADERS_ON_REDIRECT`) — are stripped by default, as expected.

However, cross-origin redirects followed from the low-level API via `ProxyManager.connection_from_url().urlopen(..., assert_same_host=False)` still forward these sensitive headers.

### Affected usage

Applications and libraries using urllib3 versions earlier than 2.7.0 may be affected if they allow cross-origin redirects while making requests through `HTTPConnection.urlopen()` instances created via `ProxyManager.connection_from_url()`.

### Remediation

Upgrade to urllib3 version 2.7.0 or later, in which sensitive headers are stripped from redirects followed by `HTTPConnection`.

If upgrading is not immediately possible, avoid using this low-level redirect flow for cross-origin redirects. If appropriate for your use case, switch to `ProxyManager.request()`.

## References
- https://github.com/urllib3/urllib3/security/advisories/GHSA-qccp-gfcp-xxvc
- https://nvd.nist.gov/vuln/detail/CVE-2026-44431
- https://github.com/urllib3/urllib3
