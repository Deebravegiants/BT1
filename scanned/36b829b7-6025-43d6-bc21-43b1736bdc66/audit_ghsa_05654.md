# [M] AIOHTTP vulnerable to DoS through chunked messages

## Summary
Severity: Medium
Advisory: GHSA-g84x-mcqj-x9qq
CVE: CVE-2025-69229
CWE: CWE-770
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N/E:U (CVSS_V4)
Published: 2026-01-05
Source: https://github.com/advisories/GHSA-g84x-mcqj-x9qq
Type: github-advisory

## Affected
- PyPI: `aiohttp` — affected >=0 <3.13.3

## Details
### Summary

Handling of chunked messages can result in excessive blocking CPU usage when receiving a large number of chunks.

### Impact

If an application makes use of the `request.read()` method in an endpoint, it may be possible for an attacker to cause the server to spend a moderate amount of blocking CPU time (e.g. 1 second) while processing the request. This could potentially lead to DoS as the server would be unable to handle other requests during that time.

-----

Patch: https://github.com/aio-libs/aiohttp/commit/dc3170b56904bdf814228fae70a5501a42a6c712
Patch: https://github.com/aio-libs/aiohttp/commit/4ed97a4e46eaf61bd0f05063245f613469700229

## References
- https://github.com/aio-libs/aiohttp/security/advisories/GHSA-g84x-mcqj-x9qq
- https://nvd.nist.gov/vuln/detail/CVE-2025-69229
- https://github.com/aio-libs/aiohttp/commit/4ed97a4e46eaf61bd0f05063245f613469700229
- https://github.com/aio-libs/aiohttp/commit/dc3170b56904bdf814228fae70a5501a42a6c712
- https://github.com/aio-libs/aiohttp
