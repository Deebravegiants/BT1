# [M] aiohttp: HTTP/1 Pipelined Requests Queue Without Limit

## Summary
Severity: Medium
Advisory: GHSA-4fvr-rgm6-gqmc
CVE: CVE-2026-54273
CWE: CWE-770
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N/E:U (CVSS_V4)
Published: 2026-06-15
Source: https://github.com/advisories/GHSA-4fvr-rgm6-gqmc
Type: github-advisory

## Affected
- PyPI: `aiohttp` — affected >=0 <3.14.1

## Details
### Summary

No limit was present on the number of pipelined requests that could be queued.

### Impact

An attacker may be able to use pipelined requests to use excessive amounts of memory, potentially leading to DoS.

-----

Patch: https://github.com/aio-libs/aiohttp/commit/dfdfa9d5aad5d21f91c79fb2ceeba0f8046cb6cf

## References
- https://github.com/aio-libs/aiohttp/security/advisories/GHSA-4fvr-rgm6-gqmc
- https://github.com/aio-libs/aiohttp/commit/dfdfa9d5aad5d21f91c79fb2ceeba0f8046cb6cf
- https://github.com/aio-libs/aiohttp
