# [M] AIOHTTP has a Multipart Header Size Bypass

## Summary
Severity: Medium
Advisory: GHSA-m5qp-6w8w-w647
CVE: CVE-2026-34516
CWE: CWE-770
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-04-01
Source: https://github.com/advisories/GHSA-m5qp-6w8w-w647
Type: github-advisory

## Affected
- PyPI: `aiohttp` — affected >=0 <3.13.4

## Details
### Summary

A response with an excessive number of multipart headers may be allowed to use more memory than intended, potentially allowing a DoS vulnerability.

### Impact

Multipart headers were not subject to the same size restrictions in place for normal headers, potentially allowing substantially more data to be loaded into memory than intended. However, other restrictions in place limit the impact of this vulnerability.

-----

Patch: https://github.com/aio-libs/aiohttp/commit/8a74257b3804c9aac0bf644af93070f68f6c5a6f

## References
- https://github.com/aio-libs/aiohttp/security/advisories/GHSA-m5qp-6w8w-w647
- https://nvd.nist.gov/vuln/detail/CVE-2026-34516
- https://github.com/aio-libs/aiohttp/commit/8a74257b3804c9aac0bf644af93070f68f6c5a6f
- https://github.com/aio-libs/aiohttp
- https://github.com/aio-libs/aiohttp/releases/tag/v3.13.4
