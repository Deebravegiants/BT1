# [M] AIOHTTP accepts duplicate Host headers

## Summary
Severity: Medium
Advisory: GHSA-c427-h43c-vf67
CVE: CVE-2026-34525
CWE: CWE-20, CWE-444
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:H/AT:P/PR:N/UI:N/VC:N/VI:L/VA:N/SC:L/SI:L/SA:N (CVSS_V4)
Published: 2026-04-01
Source: https://github.com/advisories/GHSA-c427-h43c-vf67
Type: github-advisory

## Affected
- PyPI: `aiohttp` — affected >=0 <3.13.4

## Details
### Summary

Multiple Host headers were allowed in aiohttp.

### Impact

Mostly this doesn't affect aiohttp security itself, but if a reverse proxy is applying security rules depending on the target Host, it is theoretically possible that the proxy and aiohttp could process different host names, possibly resulting in bypassing a security check on the proxy and getting a request processed by aiohttp in a privileged sub app when using `Application.add_domain()`.

-----

Patch: https://github.com/aio-libs/aiohttp/commit/e00ca3cca92c465c7913c4beb763a72da9ed8349
Patch: https://github.com/aio-libs/aiohttp/commit/53e2e6fc58b89c6185be7820bd2c9f40216b3000

## References
- https://github.com/aio-libs/aiohttp/security/advisories/GHSA-c427-h43c-vf67
- https://nvd.nist.gov/vuln/detail/CVE-2026-34525
- https://github.com/aio-libs/aiohttp/commit/53e2e6fc58b89c6185be7820bd2c9f40216b3000
- https://github.com/aio-libs/aiohttp/commit/e00ca3cca92c465c7913c4beb763a72da9ed8349
- https://github.com/aio-libs/aiohttp
- https://github.com/aio-libs/aiohttp/releases/tag/v3.13.4
