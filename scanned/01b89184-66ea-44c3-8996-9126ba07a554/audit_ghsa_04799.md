# [M] aiohttp: Incomplete websocket frame payloads bypass memory limits

## Summary
Severity: Medium
Advisory: GHSA-xcgm-r5h9-7989
CVE: CVE-2026-54274
CWE: CWE-770
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N/E:U (CVSS_V4)
Published: 2026-06-15
Source: https://github.com/advisories/GHSA-xcgm-r5h9-7989
Type: github-advisory

## Affected
- PyPI: `aiohttp` — affected >=0 <3.14.1

## Details
### Summary

If an attacker sends large incomplete websocket frame payloads, it may be possible to bypass the usual size limits on memory use.

### Impact

If a web application has WebSocket endpoints, it may be possible for an attacker to execute a DoS attack through excessive memory use.

-----

Patch: https://github.com/aio-libs/aiohttp/commit/14b6ee851fb16ec199acb950de0c82d476799e7d

## References
- https://github.com/aio-libs/aiohttp/security/advisories/GHSA-xcgm-r5h9-7989
- https://github.com/aio-libs/aiohttp
