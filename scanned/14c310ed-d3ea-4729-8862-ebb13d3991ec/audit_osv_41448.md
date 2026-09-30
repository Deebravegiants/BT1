# [M] Corteza 2024.9.8 - SQL Injection in MSSQL JSON-path meta filter via incorrect T-SQL string escaping

## Summary
Severity: Medium
Advisory: CVE-2026-6093
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:H/VI:L/VA:N/SC:N/SI:N/SA:N)
Published: 2026-05-11
Source: https://osv.dev/vulnerability/CVE-2026-6093
Type: osv

## Details
Corteza contains a SQL injection vulnerability in its Microsoft SQL Server (MSSQL) backend when filtering Compose records by the meta field.This issue affects corteza: 2024.9.8.

## References
- https://fluidattacks.com/es/advisories/motley
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/6xxx/CVE-2026-6093.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-6093
- https://github.com/cortezaproject/corteza
