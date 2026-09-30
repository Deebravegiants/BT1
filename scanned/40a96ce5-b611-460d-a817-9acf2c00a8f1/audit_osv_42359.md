# [C] FreeRDP Windows Client before 3.29.0 Heap Buffer Overflow via Cliprdr

## Summary
Severity: Critical
Advisory: CVE-2026-67305
Aliases: GHSA-cj9v-h4hq-29jr
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H)
Published: 2026-08-01
Source: https://osv.dev/vulnerability/CVE-2026-67305
Type: osv

## Details
FreeRDP Windows client before 3.29.0 contains a heap buffer overflow vulnerability in the clipboard virtual channel when processing CLIPRDR_FILE_CONTENTS_RESPONSE PDUs without validating the server-provided size against the destination buffer. A malicious RDP server can send a response with a data payload significantly larger than requested, causing arbitrary heap memory corruption that may enable remote code execution when a user performs a paste operation.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/67xxx/CVE-2026-67305.json
- https://github.com/FreeRDP/FreeRDP/security/advisories/GHSA-cj9v-h4hq-29jr
- https://nvd.nist.gov/vuln/detail/CVE-2026-67305
- https://www.vulncheck.com/advisories/freerdp-windows-client-before-heap-buffer-overflow-via-cliprdr
