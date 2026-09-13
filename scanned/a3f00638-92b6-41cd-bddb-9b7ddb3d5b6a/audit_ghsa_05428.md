# [M] AIOHTTP vulnerable to  denial of service through large payloads

## Summary
Severity: Medium
Advisory: GHSA-6jhg-hg63-jvvf
CVE: CVE-2025-69228
CWE: CWE-770
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N/E:U (CVSS_V4)
Published: 2026-01-05
Source: https://github.com/advisories/GHSA-6jhg-hg63-jvvf
Type: github-advisory

## Affected
- PyPI: `aiohttp` — affected >=0 <3.13.3

## Details
### Summary
A request can be crafted in such a way that an aiohttp server's memory fills up uncontrollably during processing.

### Impact
If an application includes a handler that uses the `Request.post()` method, an attacker may be able to freeze the server by exhausting the memory.

-----

Patch: https://github.com/aio-libs/aiohttp/commit/b7dbd35375aedbcd712cbae8ad513d56d11cce60

## References
- https://github.com/aio-libs/aiohttp/security/advisories/GHSA-6jhg-hg63-jvvf
- https://nvd.nist.gov/vuln/detail/CVE-2025-69228
- https://github.com/aio-libs/aiohttp/commit/b7dbd35375aedbcd712cbae8ad513d56d11cce60
- https://github.com/aio-libs/aiohttp
