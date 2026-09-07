# [M] AIOHTTP vulnerable to DoS when bypassing asserts

## Summary
Severity: Medium
Advisory: GHSA-jj3x-wxrx-4x23
CVE: CVE-2025-69227
CWE: CWE-835
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N/E:U (CVSS_V4)
Published: 2026-01-05
Source: https://github.com/advisories/GHSA-jj3x-wxrx-4x23
Type: github-advisory

## Affected
- PyPI: `aiohttp` — affected >=0 <3.13.3

## Details
### Summary
When assert statements are bypassed, an infinite loop can occur, resulting in a DoS attack when processing a POST body.

### Impact
If optimisations are enabled (`-O` or `PYTHONOPTIMIZE=1`), and the application includes a handler that uses the `Request.post()` method, then an attacker may be able to execute a DoS attack with a specially crafted message.

------

Patch: https://github.com/aio-libs/aiohttp/commit/bc1319ec3cbff9438a758951a30907b072561259

## References
- https://github.com/aio-libs/aiohttp/security/advisories/GHSA-jj3x-wxrx-4x23
- https://nvd.nist.gov/vuln/detail/CVE-2025-69227
- https://github.com/aio-libs/aiohttp/commit/bc1319ec3cbff9438a758951a30907b072561259
- https://github.com/aio-libs/aiohttp
