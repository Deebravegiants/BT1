# [M] MantisBT SQL Injection via mc_project_get_users function

## Summary
Severity: Medium
Advisory: GHSA-49w9-82cj-xr48
CVE: CVE-2020-28413
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-49w9-82cj-xr48
Type: github-advisory

## Affected
- Packagist: `mantisbt/mantisbt` — affected >=0 <2.24.4

## Details
In MantisBT 2.24.3, SQL Injection can occur in the parameter "access" of the mc_project_get_users function through the API SOAP.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-28413
- https://github.com/mantisbt/mantisbt/commit/3e37b4041bf76422541836a424ca71bc4a660247
- https://ethicalhcop.medium.com/cve-2020-28413-blind-sql-injection-en-mantis-bug-tracker-2-24-3-api-soap-54238f8e046d
- https://github.com/mantisbt/mantisbt
- http://packetstormsecurity.com/files/160750/Mantis-Bug-Tracker-2.24.3-SQL-Injection.html
