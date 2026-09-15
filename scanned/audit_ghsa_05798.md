# [M] AIOHTTP: WebSocket client accepts compressed frames without negotiated permessage-deflate

## Summary
Severity: Medium
Advisory: GHSA-mq44-7p77-q5h7
CVE: CVE-2026-59881
CWE: CWE-20
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-08-03
Source: https://github.com/advisories/GHSA-mq44-7p77-q5h7
Type: github-advisory

## Affected
- PyPI: `aiohttp` — affected >=0 <3.14.2

## Details
### Summary

The client accepts and decompresses frames with the RSV1 bit set even when the `permessage-deflate` extension was not negotiated.

### Impact

A client may unexpectedly decompress WebSocket frames when explicitly opted out. This could lead to additional CPU/memory consumption, but is unlikely to be a significant issue unless a zip bomb vulnerability or similar is also present.

---

Patch: https://github.com/aio-libs/aiohttp/commit/47fb6ae354d4fa22048f4dbe7dbf82b625f0a2f6

## References
- https://github.com/aio-libs/aiohttp/security/advisories/GHSA-mq44-7p77-q5h7
- https://nvd.nist.gov/vuln/detail/CVE-2026-59881
- https://github.com/aio-libs/aiohttp/pull/12978
- https://github.com/aio-libs/aiohttp/commit/47fb6ae354d4fa22048f4dbe7dbf82b625f0a2f6
- https://github.com/aio-libs/aiohttp
- http://github.com/aio-libs/aiohttp/releases/tag/v3.14.2
