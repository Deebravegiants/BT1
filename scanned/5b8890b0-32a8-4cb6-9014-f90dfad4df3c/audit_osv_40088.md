# [M] OpenCATS - SQL Injection in DataGrid sortDirection Parameter

## Summary
Severity: Medium
Advisory: CVE-2026-49489
Aliases: GHSA-8mc8-5gw6-c7w4
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:L/SC:H/SI:N/SA:L)
Published: 2026-05-31
Source: https://osv.dev/vulnerability/CVE-2026-49489
Type: osv

## Details
OpenCATS through 0.9.7.4 contains a sql injection vulnerability in the sortDirection parameter of the DataGrid component that allows authenticated users to extract database contents. Attackers can inject malicious SQL via the sortDirection parameter in ajax/getDataGridPager.php to perform time-based blind injection attacks and read sensitive data.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/49xxx/CVE-2026-49489.json
- https://github.com/opencats/OpenCATS/security/advisories/GHSA-8mc8-5gw6-c7w4
- https://nvd.nist.gov/vuln/detail/CVE-2026-49489
- https://www.vulncheck.com/advisories/opencats-sql-injection-in-datagrid-sortdirection-parameter
- https://packetstorm.news/files/id/222200/
- https://www.exploit-db.com/exploits/52579
