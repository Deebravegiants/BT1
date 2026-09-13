# [C] FreeRDP has a heap-buffer-overflow in audin_process_formats

## Summary
Severity: Critical
Advisory: CVE-2026-22852
Aliases: GHSA-9chc-g79v-4qq4
CVSS: 9.0 (CVSS:4.0/AV:N/AC:H/AT:N/PR:N/UI:P/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:P)
Published: 2026-01-14
Source: https://osv.dev/vulnerability/CVE-2026-22852
Type: osv

## Details
FreeRDP is a free implementation of the Remote Desktop Protocol. Prior to 3.20.1, a malicious RDP server can trigger a heap-buffer-overflow write in the FreeRDP client when processing Audio Input (AUDIN) format lists. audin_process_formats reuses callback->formats_count across multiple MSG_SNDIN_FORMATS PDUs and writes past the newly allocated formats array, causing memory corruption and a crash. This vulnerability is fixed in 3.20.1.

## References
- https://github.com/FreeRDP/FreeRDP/releases/tag/3.20.1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/22xxx/CVE-2026-22852.json
- https://github.com/FreeRDP/FreeRDP/security/advisories/GHSA-9chc-g79v-4qq4
- https://nvd.nist.gov/vuln/detail/CVE-2026-22852
