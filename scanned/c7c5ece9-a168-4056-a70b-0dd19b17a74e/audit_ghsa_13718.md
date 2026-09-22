# [M] aiohttp has vulnerable dependency that is vulnerable to request smuggling

## Summary
Severity: Medium
Advisory: GHSA-pjjw-qhg8-p2p9
CWE: CWE-444
Ecosystem: PyPI
Published: 2023-11-27
Source: https://github.com/advisories/GHSA-pjjw-qhg8-p2p9
Type: github-advisory

## Affected
- PyPI: `aiohttp` — affected >=0 <3.8.6

## Details
### Summary
llhttp 8.1.1 is vulnerable to two request smuggling vulnerabilities.
Details have not been disclosed yet, so refer to llhttp for future information.
The issue is resolved by using llhttp 9+ (which is included in aiohttp 3.8.6+).

## References
- https://github.com/aio-libs/aiohttp/security/advisories/GHSA-pjjw-qhg8-p2p9
- https://github.com/aio-libs/aiohttp/commit/996de2629ef6b4c2934a7c04dfd49d0950d4c43b
- https://github.com/aio-libs/aiohttp/commit/bcc416e533796d04fb8124ef1e7686b1f338767a
- https://github.com/aio-libs/aiohttp
