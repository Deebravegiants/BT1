# [M] FreeRDP: Smartcard NDR Alignment Padding Triggers Reachable WINPR_ASSERT Abort (Client DoS)

## Summary
Severity: Medium
Advisory: CVE-2026-27015
Aliases: GHSA-7g72-39pq-4725
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:A/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N/E:P)
Published: 2026-02-25
Source: https://osv.dev/vulnerability/CVE-2026-27015
Type: osv

## Details
FreeRDP is a free implementation of the Remote Desktop Protocol. Prior to version 3.23.0, a missing bounds check in `smartcard_unpack_read_size_align()` (`libfreerdp/utils/smartcard_pack.c:1703`) allows a malicious RDP server to crash the FreeRDP client via a reachable `WINPR_ASSERT` → `abort()`. The crash occurs in upstream builds where `WITH_VERBOSE_WINPR_ASSERT=ON` (default in FreeRDP 3.22.0 / current WinPR CMake defaults). Smartcard redirection must be explicitly enabled by the user (e.g., `xfreerdp /smartcard`; `/smartcard-logon` implies `/smartcard`). Version 3.23.0 fixes the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/27xxx/CVE-2026-27015.json
- https://github.com/FreeRDP/FreeRDP/security/advisories/GHSA-7g72-39pq-4725
- https://nvd.nist.gov/vuln/detail/CVE-2026-27015
- https://github.com/FreeRDP/FreeRDP/commit/65d59d3b3c2f630f2ea862687ecf5f95f8115244
