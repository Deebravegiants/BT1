# [M] FreeRDP has a heap-use-after-free in ainput_send_input_event

## Summary
Severity: Medium
Advisory: CVE-2026-24683
Aliases: GHSA-45pf-68pj-fg8q
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-02-09
Source: https://osv.dev/vulnerability/CVE-2026-24683
Type: osv

## Details
FreeRDP is a free implementation of the Remote Desktop Protocol. ainput_send_input_event caches channel_callback in a local variable and later uses it without synchronization; a concurrent channel close can free or reinitialize the callback, leading to a use after free. Prior to 3.22.0, This vulnerability is fixed in 3.22.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/24xxx/CVE-2026-24683.json
- https://github.com/FreeRDP/FreeRDP/security/advisories/GHSA-45pf-68pj-fg8q
- https://nvd.nist.gov/vuln/detail/CVE-2026-24683
- https://github.com/FreeRDP/FreeRDP/commit/d9ca272dce7a776ab475e9b1a8e8c3d2968c8486
