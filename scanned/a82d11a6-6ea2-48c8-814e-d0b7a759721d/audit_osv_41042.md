# [C] FreeRDP: Integer overflow leading to heap buffer overflow in Orders Delta Points parsing

## Summary
Severity: Critical
Advisory: CVE-2026-57156
Aliases: GHSA-v5wf-j8j4-77h7
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:A/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-07-10
Source: https://osv.dev/vulnerability/CVE-2026-57156
Type: osv

## Details
FreeRDP is a free implementation of the Remote Desktop Protocol. Prior to 3.28.0 on 32-bit builds, FreeRDP clients contain an integer overflow in update_read_delta_points in libfreerdp/core/orders.c when multiplying an attacker-controlled point count by sizeof(DELTA_POINT), allowing a malicious RDP peer to allocate an undersized heap buffer and then write beyond it during initialization. This issue is fixed in version 3.28.0.

## References
- https://github.com/FreeRDP/FreeRDP/releases/tag/3.28.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/57xxx/CVE-2026-57156.json
- https://github.com/FreeRDP/FreeRDP/security/advisories/GHSA-v5wf-j8j4-77h7
- https://nvd.nist.gov/vuln/detail/CVE-2026-57156
- https://github.com/FreeRDP/FreeRDP/commit/487f35daccb36a6224e530dcd8fa60850825f823
- https://github.com/FreeRDP/FreeRDP/pull/12938
