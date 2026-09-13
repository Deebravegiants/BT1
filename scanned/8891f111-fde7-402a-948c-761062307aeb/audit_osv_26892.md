# [M] WorkOrder CMS 0.1.0 - SQL Injection

## Summary
Severity: Medium
Advisory: CVE-2023-54340
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:L/VA:N/SC:N/SI:N/SA:N)
Published: 2026-01-13
Source: https://osv.dev/vulnerability/CVE-2023-54340
Type: osv

## Details
WorkOrder CMS 0.1.0 contains a SQL injection vulnerability that allows unauthenticated attackers to bypass login by manipulating username and password parameters. Attackers can inject malicious SQL queries using techniques like OR '1'='1' and stacked queries to access database information or execute administrative commands.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/54xxx/CVE-2023-54340.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-54340
- https://www.vulncheck.com/advisories/workorder-cms-sql-injection
- https://github.com/romzes13/WorkOrderCMS
- https://www.exploit-db.com/exploits/51038
