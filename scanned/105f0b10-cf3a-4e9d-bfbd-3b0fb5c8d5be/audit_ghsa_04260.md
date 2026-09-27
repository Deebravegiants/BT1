# [M] AIOHTTP is vulnerable to cross-origin redirect with per-request cookies

## Summary
Severity: Medium
Advisory: GHSA-hg6j-4rv6-33pg
CVE: CVE-2026-47265
CWE: CWE-346
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N/E:U (CVSS_V4)
Published: 2026-06-03
Source: https://github.com/advisories/GHSA-hg6j-4rv6-33pg
Type: github-advisory

## Affected
- PyPI: `aiohttp` — affected >=0 <3.14.0

## Details
### Summary

Cookies set with the `cookies` parameter on requests are sent after following a cross-origin redirect.

### Impact

If a developer uses the `cookies` parameter on a per-request basis then sensitive data might be leaked to an attacker if they manage to control a redirect.

### Workaround

If unable to upgrade, using a `Cookie` header in the `headers` parameter is not vulnerable.

-----

Patch: https://github.com/aio-libs/aiohttp/commit/f54c40851b0d6c4bbdab97ba518a223adda32478

## References
- https://github.com/aio-libs/aiohttp/security/advisories/GHSA-hg6j-4rv6-33pg
- https://nvd.nist.gov/vuln/detail/CVE-2026-47265
- https://github.com/aio-libs/aiohttp/commit/f54c40851b0d6c4bbdab97ba518a223adda32478
- https://github.com/aio-libs/aiohttp
