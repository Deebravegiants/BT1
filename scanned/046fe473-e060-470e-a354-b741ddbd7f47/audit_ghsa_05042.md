# [M] aiohttp: C HTTP Parser Bypasses max_line_size for Fragmented Lines

## Summary
Severity: Medium
Advisory: GHSA-63hw-fmq6-xxg2
CVE: CVE-2026-54277
CWE: CWE-770
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N/E:U (CVSS_V4)
Published: 2026-06-15
Source: https://github.com/advisories/GHSA-63hw-fmq6-xxg2
Type: github-advisory

## Affected
- PyPI: `aiohttp` — affected >=0 <3.14.1

## Details
### Summary

It is possible to bypass the max_line_size check in parts of an HTTP request in the C parser.

### Impact

If using the optimised C parser (the default in pre-built wheels), then an attacker may be able to send oversized lines through the HTTP parser and use an excessive amount of memory, potentially leading to DoS.

-----

Patch: https://github.com/aio-libs/aiohttp/commit/5ab61bb4cd88f19b712f12c7c9295fe262bf804d

## References
- https://github.com/aio-libs/aiohttp/security/advisories/GHSA-63hw-fmq6-xxg2
- https://github.com/aio-libs/aiohttp/commit/5ab61bb4cd88f19b712f12c7c9295fe262bf804d
- https://github.com/aio-libs/aiohttp
