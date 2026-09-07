# [M] aiohttp: Unread Compressed Request Bodies Bypass client_max_size During Cleanup

## Summary
Severity: Medium
Advisory: GHSA-g3cq-j2xw-wf74
CVE: CVE-2026-54278
CWE: CWE-409
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N/E:U (CVSS_V4)
Published: 2026-06-15
Source: https://github.com/advisories/GHSA-g3cq-j2xw-wf74
Type: github-advisory

## Affected
- PyPI: `aiohttp` — affected >=0 <3.14.1

## Details
### Summary

During cleanup it is possible for a compressed request body to be decompressed into memory in one chunk.

### Impact

An attacker may be able to send a compressed payload in specific situations that could be decompressed into memory, potentially leading to DoS (a zip bomb edge case).

### Workaround

Disable compression if unable to upgrade.

-----

Patch: https://github.com/aio-libs/aiohttp/commit/4f7480e474cccc6a8cc2c92ad3f17a31dedf8232

## References
- https://github.com/aio-libs/aiohttp/security/advisories/GHSA-g3cq-j2xw-wf74
- https://github.com/aio-libs/aiohttp
