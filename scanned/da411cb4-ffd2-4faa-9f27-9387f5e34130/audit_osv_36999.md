# [M] NanaZip .NET Single-File Parser Integer Underflow Leads to Unbounded Allocation (DoS)

## Summary
Severity: Medium
Advisory: CVE-2026-27710
Aliases: GHSA-89qw-8p49-32wf
CVSS: 6.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:L/UI:P/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-02-25
Source: https://osv.dev/vulnerability/CVE-2026-27710
Type: osv

## Details
NanaZip is an open source file archive. Starting in version 5.0.1252.0 and prior to versions 6.0.1638.0 and 6.5.1638.0, a denial-of-service vulnerability exists in NanaZip’s `.NET Single File Application` parser. A crafted bundle can force an integer underflow in header-size calculation and trigger an unbounded memory allocation attempt during archive open. Versions 6.0.1638.0 and 6.5.1638.0 fix the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/27xxx/CVE-2026-27710.json
- https://github.com/M2Team/NanaZip/security/advisories/GHSA-89qw-8p49-32wf
- https://nvd.nist.gov/vuln/detail/CVE-2026-27710
