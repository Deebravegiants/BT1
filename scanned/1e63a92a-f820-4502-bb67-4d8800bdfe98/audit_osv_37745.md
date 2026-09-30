# [C] DataEase has SQL Injection through its getFieldEnumObj Endpoint

## Summary
Severity: Critical
Advisory: CVE-2026-33084
Aliases: GHSA-r897-r9q8-3p2x
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-04-16
Source: https://osv.dev/vulnerability/CVE-2026-33084
Type: osv

## Details
DataEase is an open-source data visualization and analytics platform. Versions 2.10.20 and below contain a SQL injection vulnerability in the sort parameter of the /de2api/datasetData/enumValueObj endpoint. The DatasetDataManage service layer directly transfers the user-supplied sort value to the sorting metadata DTO, which is passed to Order2SQLObj where it is incorporated into the SQL ORDER BY clause without any whitelist validation, and then executed via CalciteProvider. An authenticated attacker can inject arbitrary SQL commands through the sort parameter, enabling time-based blind SQL injection. This issue has been fixed in version 2.10.21.

## References
- https://github.com/dataease/dataease/releases/tag/v2.10.21
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/33xxx/CVE-2026-33084.json
- https://github.com/dataease/dataease/security/advisories/GHSA-r897-r9q8-3p2x
- https://nvd.nist.gov/vuln/detail/CVE-2026-33084
