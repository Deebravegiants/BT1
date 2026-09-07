# [C] SQL Injection in knex

## Summary
Severity: Critical
Advisory: GHSA-58v4-qwx5-7f59
CVE: CVE-2019-10757
CWE: CWE-89
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2019-10-21
Source: https://github.com/advisories/GHSA-58v4-qwx5-7f59
Type: github-advisory

## Affected
- npm: `knex` — affected >=0 <0.19.5

## Details
knex.js versions before 0.19.5 are vulnerable to SQL Injection attack. Identifiers are escaped incorrectly as part of the MSSQL dialect, allowing attackers to craft a malicious query to the host DB.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10757
- https://snyk.io/vuln/SNYK-JS-KNEX-471962
