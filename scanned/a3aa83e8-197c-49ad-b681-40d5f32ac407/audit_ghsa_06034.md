# [M] AIOHTTP: HTTP request smuggling via WebSocket upgrade

## Summary
Severity: Medium
Advisory: GHSA-mfx4-hv73-q22v
CVE: CVE-2026-69243
CWE: CWE-444
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:H/AT:N/PR:N/UI:N/VC:N/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-08-03
Source: https://github.com/advisories/GHSA-mfx4-hv73-q22v
Type: github-advisory

## Affected
- PyPI: `aiohttp` — affected >=0 <3.14.2

## Details
### Summary

The HTTP parsers were vulnerable to a request smuggling attack relating to WebSocket upgrades.

### Impact

If using the server-side component, it may be possible for an attacker to execute a request smuggling vulnerability using an edge case in the WebSocket upgrade procedure. AIOHTT is unaware of any public exploit code.

---

Patch: https://github.com/aio-libs/aiohttp/commit/6ae358f0983c3f4d6f67692b2f8e65dc8e091c98

## References
- https://github.com/aio-libs/aiohttp/security/advisories/GHSA-mfx4-hv73-q22v
- https://github.com/aio-libs/aiohttp/pull/13017
- https://github.com/aio-libs/aiohttp/commit/6ae358f0983c3f4d6f67692b2f8e65dc8e091c98
- https://github.com/aio-libs/aiohttp
- https://github.com/aio-libs/aiohttp/releases/tag/v3.14.2
