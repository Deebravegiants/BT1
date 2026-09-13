# [C] FreeRDP has a heap-buffer-overflow in ndr_read_uint8Array

## Summary
Severity: Critical
Advisory: CVE-2026-22853
Aliases: GHSA-47v9-p4gp-w5ch
CVSS: 9.0 (CVSS:4.0/AV:N/AC:H/AT:N/PR:N/UI:P/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:P)
Published: 2026-01-14
Source: https://osv.dev/vulnerability/CVE-2026-22853
Type: osv

## Details
FreeRDP is a free implementation of the Remote Desktop Protocol. Prior to 3.20.1, RDPEAR’s NDR array reader does not perform bounds checking on the on‑wire element count and can write past the heap buffer allocated from hints, causing a heap buffer overflow in ndr_read_uint8Array. This vulnerability is fixed in 3.20.1.

## References
- https://github.com/FreeRDP/FreeRDP/releases/tag/3.20.1
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-22853.json
- https://access.redhat.com/errata/RHSA-2026:19033
- https://access.redhat.com/errata/RHSA-2026:3068
- https://access.redhat.com/errata/RHSA-2026:4121
- https://access.redhat.com/security/cve/CVE-2026-22853
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/22xxx/CVE-2026-22853.json
- https://github.com/FreeRDP/FreeRDP/security/advisories/GHSA-47v9-p4gp-w5ch
- https://nvd.nist.gov/vuln/detail/CVE-2026-22853
- https://bugzilla.redhat.com/show_bug.cgi?id=2429647
