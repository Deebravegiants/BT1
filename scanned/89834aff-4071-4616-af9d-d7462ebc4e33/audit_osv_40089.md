# [H] OpenCATS - SQL Injection in DataGrid Filter Handling for Tags Column

## Summary
Severity: High
Advisory: CVE-2026-49490
Aliases: GHSA-gmpc-j6h7-vw74
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-05-31
Source: https://osv.dev/vulnerability/CVE-2026-49490
Type: osv

## Details
OpenCATS from version 0.9.1a contains an SQL injection vulnerability in DataGrid filter handling that allows authenticated attackers to inject SQL through crafted filters targeting the non-filterable Tags column in the Candidates DataGrid. Attackers can bypass column filterable restrictions by manipulating filter requests to execute arbitrary SQL queries against the database.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/49xxx/CVE-2026-49490.json
- https://github.com/opencats/OpenCATS/security/advisories/GHSA-gmpc-j6h7-vw74
- https://nvd.nist.gov/vuln/detail/CVE-2026-49490
- https://www.vulncheck.com/advisories/opencats-sql-injection-in-datagrid-filter-handling-for-tags-column
