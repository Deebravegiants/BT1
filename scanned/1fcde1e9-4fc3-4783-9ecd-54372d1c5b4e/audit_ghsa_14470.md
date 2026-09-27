# [C] SQL Injection in Funadmin

## Summary
Severity: Critical
Advisory: GHSA-7pmh-8qjj-4q36
CVE: CVE-2023-24780
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-03-08
Source: https://github.com/advisories/GHSA-7pmh-8qjj-4q36
Type: github-advisory

## Affected
- Packagist: `funadmin/funadmin` — affected >=0

## Details
Funadmin v3.2.0 was discovered to contain a SQL injection vulnerability via the id parameter at /databases/table/columns.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-24780
- https://github.com/funadmin/funadmin/issues/6
