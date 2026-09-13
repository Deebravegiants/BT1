# [M] NASA Core Flight System (cFS) Health & Safety (HS) Application NULL Pointer Dereference

## Summary
Severity: Medium
Advisory: CVE-2026-15352
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-07-16
Source: https://osv.dev/vulnerability/CVE-2026-15352
Type: osv

## Details
A vulnerability exists in the Health & Safety (HS) application of NASA's Core Flight System (cFS). The flaw allows the application to crash via segmentation fault when processing a routine Housekeeping Telemetry request, leading to denial of service.

## References
- https://github.com/cisagov/CSAF/blob/develop/csaf_files/OT/white/2026/icsa-26-197-03.json
- https://github.com/nasa/HS/releases/tag/v7.0.1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/15xxx/CVE-2026-15352.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-15352
- https://www.cisa.gov/news-events/ics-advisories/icsa-26-197-03
