# [M] aiohttp has a memory leak when middleware is enabled when requesting a resource with a non-allowed method

## Summary
Severity: Medium
Advisory: GHSA-27mf-ghqm-j3j8
CVE: CVE-2024-52303
CWE: CWE-772
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2024-11-18
Source: https://github.com/advisories/GHSA-27mf-ghqm-j3j8
Type: github-advisory

## Affected
- PyPI: `aiohttp` — affected >=3.10.6 <3.10.11

## Details
### Summary

A memory leak can occur when a request produces a `MatchInfoError`. This was caused by adding an entry to a cache on each request, due to the building of each `MatchInfoError` producing a unique cache entry.

### Impact

If the user is making use of any middlewares with `aiohttp.web` then it is advisable to upgrade immediately.

An attacker may be able to exhaust the memory resources of a server by sending a substantial number (100,000s to millions) of such requests.

-----

Patch: https://github.com/aio-libs/aiohttp/commit/bc15db61615079d1b6327ba42c682f758fa96936

## References
- https://github.com/aio-libs/aiohttp/security/advisories/GHSA-27mf-ghqm-j3j8
- https://nvd.nist.gov/vuln/detail/CVE-2024-52303
- https://github.com/aio-libs/aiohttp/commit/bc15db61615079d1b6327ba42c682f758fa96936
- https://github.com/aio-libs/aiohttp
