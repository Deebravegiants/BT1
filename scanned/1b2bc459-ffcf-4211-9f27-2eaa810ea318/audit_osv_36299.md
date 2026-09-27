# [C] FreeRDP has a heap-buffer-overflow in drive_process_irp_read

## Summary
Severity: Critical
Advisory: CVE-2026-22854
Aliases: GHSA-47vj-g3c3-3rmf
CVSS: 9.0 (CVSS:4.0/AV:N/AC:H/AT:N/PR:N/UI:P/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:P)
Published: 2026-01-14
Source: https://osv.dev/vulnerability/CVE-2026-22854
Type: osv

## Details
FreeRDP is a free implementation of the Remote Desktop Protocol. Prior to 3.20.1, a heap-buffer-overflow occurs in drive read when a server-controlled read length is used to read file data into an IRP output stream buffer without a hard upper bound, allowing an oversized read to overwrite heap memory. This vulnerability is fixed in 3.20.1.

## References
- https://github.com/FreeRDP/FreeRDP/releases/tag/3.20.1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/22xxx/CVE-2026-22854.json
- https://github.com/FreeRDP/FreeRDP/security/advisories/GHSA-47vj-g3c3-3rmf
- https://nvd.nist.gov/vuln/detail/CVE-2026-22854
