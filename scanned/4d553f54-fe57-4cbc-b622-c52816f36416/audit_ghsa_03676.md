# [C] SQL Injection in typeorm

## Summary
Severity: Critical
Advisory: GHSA-w7q7-vjp8-7jv4
CWE: CWE-89
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2019-06-06
Source: https://github.com/advisories/GHSA-w7q7-vjp8-7jv4
Type: github-advisory

## Affected
- npm: `typeorm` — affected >=0 <0.1.15

## Details
Versions of `typeorm` before 0.1.15 are vulnerable to SQL Injection. Field names are not properly validated allowing attackers to inject SQL statements and execute arbitrary SQL queries.


## Recommendation

Upgrade to version 0.1.15

## References
- https://github.com/typeorm/typeorm/commit/d46c8b0e6c0db56bb5976a4917e9f67a43715111
- https://hackerone.com/reports/319458
- https://github.com/typeorm/typeorm
- https://www.npmjs.com/advisories/800
