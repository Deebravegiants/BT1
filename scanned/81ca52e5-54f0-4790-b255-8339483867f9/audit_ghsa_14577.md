# [C] SQL Injection in Funadmin

## Summary
Severity: Critical
Advisory: GHSA-m8wf-wmwh-jw2m
CVE: CVE-2023-24773
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-03-08
Source: https://github.com/advisories/GHSA-m8wf-wmwh-jw2m
Type: github-advisory

## Affected
- Packagist: `funadmin/funadmin` — affected >=0

## Details
Funadmin v3.2.0 was discovered to contain a SQL injection vulnerability via the id parameter at /databases/database/list.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-24773
- https://github.com/funadmin/funadmin/issues/4
- https://github.com/funadmin/funadmin
