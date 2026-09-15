# [H] AIOHTTP's HTTP Parser auto_decompress feature is vulnerable to zip bomb

## Summary
Severity: High
Advisory: GHSA-6mq8-rvhq-8wgg
CVE: CVE-2025-69223
CWE: CWE-409, CWE-770
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-01-05
Source: https://github.com/advisories/GHSA-6mq8-rvhq-8wgg
Type: github-advisory

## Affected
- PyPI: `aiohttp` — affected >=0 <3.13.3

## Details
### Summary
A zip bomb can be used to execute a DoS against the aiohttp server.

### Impact
An attacker may be able to send a compressed request that when decompressed by aiohttp could exhaust the host's memory.

------

Patch: https://github.com/aio-libs/aiohttp/commit/2b920c39002cee0ec5b402581779bbaaf7c9138a

## References
- https://github.com/aio-libs/aiohttp/security/advisories/GHSA-6mq8-rvhq-8wgg
- https://nvd.nist.gov/vuln/detail/CVE-2025-69223
- https://github.com/aio-libs/aiohttp/commit/2b920c39002cee0ec5b402581779bbaaf7c9138a
- https://github.com/aio-libs/aiohttp
