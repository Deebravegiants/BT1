# [M] aiohttp allows unlimited trailer headers, leading to possible uncapped memory usage

## Summary
Severity: Medium
Advisory: GHSA-w2fm-2cpv-w7v5
CVE: CVE-2026-22815
CWE: CWE-400, CWE-770
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-04-01
Source: https://github.com/advisories/GHSA-w2fm-2cpv-w7v5
Type: github-advisory

## Affected
- PyPI: `aiohttp` — affected >=0 <3.13.4

## Details
### Summary

Insufficient restrictions in header/trailer handling could cause uncapped memory usage.

### Impact

An application could cause memory exhaustion when receiving an attacker controlled request or response. A vulnerable web application could mitigate these risks with a typical reverse proxy configuration.

-----

Patch: https://github.com/aio-libs/aiohttp/commit/0c2e9da51126238a421568eb7c5b53e5b5d17b36

## References
- https://github.com/aio-libs/aiohttp/security/advisories/GHSA-w2fm-2cpv-w7v5
- https://nvd.nist.gov/vuln/detail/CVE-2026-22815
- https://github.com/aio-libs/aiohttp/commit/0c2e9da51126238a421568eb7c5b53e5b5d17b36
- https://github.com/aio-libs/aiohttp
- https://github.com/aio-libs/aiohttp/releases/tag/v3.13.4
