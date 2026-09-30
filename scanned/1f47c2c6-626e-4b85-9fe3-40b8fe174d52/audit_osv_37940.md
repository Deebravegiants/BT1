# [M] FreeRDP: DoS via WINPR_ASSERT in rts_read_auth_verifier_no_checks

## Summary
Severity: Medium
Advisory: CVE-2026-33952
Aliases: GHSA-4v4p-9v5x-hc93
CVSS: 6.0 (CVSS:4.0/AV:N/AC:H/AT:N/PR:N/UI:P/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-03-30
Source: https://osv.dev/vulnerability/CVE-2026-33952
Type: osv

## Details
FreeRDP is a free implementation of the Remote Desktop Protocol. Prior to version 3.24.2, an unvalidated auth_length field read from the network triggers a WINPR_ASSERT() failure in rts_read_auth_verifier_no_checks(), causing any FreeRDP client connecting through a malicious RDP Gateway to crash with SIGABRT. This is a pre-authentication denial of service affecting all FreeRDP clients using RPC-over-HTTP gateway transport. The assertion is active in default release builds (WITH_VERBOSE_WINPR_ASSERT=ON). This issue has been patched in version 3.24.2.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/33xxx/CVE-2026-33952.json
- https://github.com/FreeRDP/FreeRDP/security/advisories/GHSA-4v4p-9v5x-hc93
- https://nvd.nist.gov/vuln/detail/CVE-2026-33952
- https://github.com/FreeRDP/FreeRDP/commit/4ac0b6467d371a1ad47c1f751c5b305e4c068adb
