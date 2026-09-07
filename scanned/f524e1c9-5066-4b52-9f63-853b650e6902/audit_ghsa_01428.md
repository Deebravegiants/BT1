# [H] SQL Injection in sails-mysql

## Summary
Severity: High
Advisory: GHSA-hx5x-49mm-vmhw
CWE: CWE-89
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2020-09-03
Source: https://github.com/advisories/GHSA-hx5x-49mm-vmhw
Type: github-advisory

## Affected
- npm: `sails-mysql` — affected >=0 <0.10.8

## Details
Versions of `sails-mysql` prior to 0.10.8 are vulnerable to SQL Injection. The `sort` keyword is not properly sanitized and may allow attackers to inject SQL statements and execute arbitrary SQL queries


## Recommendation

Upgrade to version 0.10.8 or later.

## References
- https://github.com/balderdashy/sails/issues/6679
- https://github.com/balderdashy/sails
- https://snyk.io/vuln/SNYK-JS-SAILSMYSQL-174916
- https://www.npmjs.com/advisories/950
