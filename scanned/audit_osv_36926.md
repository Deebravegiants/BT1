# [M] NanZip has ROMFS Archive Infinite Loop / Stack Overflow

## Summary
Severity: Medium
Advisory: CVE-2026-27014
Aliases: GHSA-fc89-3f57-h9q5
CVSS: 6.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:L/UI:P/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-02-19
Source: https://osv.dev/vulnerability/CVE-2026-27014
Type: osv

## Details
NanaZip is an open source file archive Starting in version 5.0.1252.0 and prior to version 6.0.1630.0, circular `NextOffset` chains cause an infinite loop, and deeply nested directories cause unbounded recursion (stack overflow) in the ROMFS archive parser. Version 6.0.1630.0 patches the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/27xxx/CVE-2026-27014.json
- https://github.com/M2Team/NanaZip/security/advisories/GHSA-fc89-3f57-h9q5
- https://nvd.nist.gov/vuln/detail/CVE-2026-27014
