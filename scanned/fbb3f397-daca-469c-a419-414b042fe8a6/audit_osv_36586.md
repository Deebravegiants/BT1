# [M] FreeRDP has a heap-use-after-free in video_timer

## Summary
Severity: Medium
Advisory: CVE-2026-24491
Aliases: GHSA-4x6j-w49r-869g
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N/E:P)
Published: 2026-02-09
Source: https://osv.dev/vulnerability/CVE-2026-24491
Type: osv

## Details
FreeRDP is a free implementation of the Remote Desktop Protocol. Prior to 3.22.0, video_timer can send client notifications after the control channel is closed, dereferencing a freed callback and triggering a use after free. This vulnerability is fixed in 3.22.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/24xxx/CVE-2026-24491.json
- https://github.com/FreeRDP/FreeRDP/security/advisories/GHSA-4x6j-w49r-869g
- https://nvd.nist.gov/vuln/detail/CVE-2026-24491
- https://github.com/FreeRDP/FreeRDP/commit/e02e052f6692550e539d10f99de9c35a23492db2
