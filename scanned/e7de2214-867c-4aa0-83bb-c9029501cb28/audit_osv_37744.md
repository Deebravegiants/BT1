# [C] DataEase has SQL Injection in Order By Clause

## Summary
Severity: Critical
Advisory: CVE-2026-33083
Aliases: GHSA-f443-95cf-m837
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-04-16
Source: https://osv.dev/vulnerability/CVE-2026-33083
Type: osv

## Details
DataEase is an open-source data visualization and analytics platform. Versions 2.10.20 and below contain a SQL injection vulnerability in the orderDirection parameter used in dataset-related endpoints including /de2api/datasetData/enumValueDs and /de2api/datasetTree/exportDataset. The Order2SQLObj class directly assigns the raw user-supplied orderDirection value into the SQL query without any validation or whitelist enforcement, and the value is rendered into the ORDER BY clause via StringTemplate before being executed against the database. An authenticated attacker can inject arbitrary SQL commands through the sorting direction field, enabling time-based blind data extraction and denial of service. This issue has been fixed in version 2.10.21.

## References
- https://github.com/dataease/dataease/releases/tag/v2.10.21
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/33xxx/CVE-2026-33083.json
- https://github.com/dataease/dataease/security/advisories/GHSA-f443-95cf-m837
- https://nvd.nist.gov/vuln/detail/CVE-2026-33083
