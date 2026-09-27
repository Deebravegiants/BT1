# [M] Excelize: Streaming GetRows row-bound bypass causes attacker-controlled allocation

## Summary
Severity: Medium
Advisory: CVE-2026-59161
Aliases: GHSA-q5j5-6p94-4gwc
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-07-10
Source: https://osv.dev/vulnerability/CVE-2026-59161
Type: osv

## Details
Excelize is a Go language library for reading and writing Microsoft Excel spreadsheets. Prior to 2.11.0, the streaming worksheet reader used by Rows and GetRows does not enforce the TotalRows limit on the row r attribute, allowing a small XLSX file with a row number above 1048576 and no cell coordinate to make GetRows append empty rows up to the attacker-controlled index and consume excessive memory and CPU. This issue is fixed in version 2.11.0.

## References
- https://github.com/qax-os/excelize/releases/tag/v2.11.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/59xxx/CVE-2026-59161.json
- https://github.com/qax-os/excelize/security/advisories/GHSA-q5j5-6p94-4gwc
- https://nvd.nist.gov/vuln/detail/CVE-2026-59161
- https://github.com/qax-os/excelize/commit/93f0b3caed37f21ef5079e3259c6c21dcfe68453
- https://github.com/qax-os/excelize/pull/2331
