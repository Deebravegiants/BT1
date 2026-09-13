# [H] DataEase has SQL Injection via Stacked Queries

## Summary
Severity: High
Advisory: CVE-2026-40900
Aliases: GHSA-vqxf-84ph-j3vx
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:L/SC:N/SI:N/SA:N)
Published: 2026-04-16
Source: https://osv.dev/vulnerability/CVE-2026-40900
Type: osv

## Details
DataEase is an open-source data visualization and analytics platform. Versions 2.10.20 and below contain a SQL injection vulnerability in the /de2api/datasetData/previewSql endpoint. The user-supplied SQL is wrapped in a subquery without validation that the input is a single SELECT statement. Combined with the JDBC blocklist bypass that allows enabling allowMultiQueries=true, an attacker can break out of the subquery and execute arbitrary stacked SQL statements, including UPDATE and other write operations, against the connected database. An authenticated attacker with access to valid datasource credentials can achieve full read and write access to the underlying database. This issue has been fixed in version 2.10.21.

## References
- https://github.com/dataease/dataease/releases/tag/v2.10.21
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/40xxx/CVE-2026-40900.json
- https://github.com/dataease/dataease/security/advisories/GHSA-vqxf-84ph-j3vx
- https://nvd.nist.gov/vuln/detail/CVE-2026-40900
