# [C] SQL Injection in sequelize

## Summary
Severity: Critical
Advisory: GHSA-2598-2f59-rmhq
CVE: CVE-2019-10749
CWE: CWE-89
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2019-11-08
Source: https://github.com/advisories/GHSA-2598-2f59-rmhq
Type: github-advisory

## Affected
- npm: `sequelize` — affected >=0 <3.35.1

## Details
Versions of `sequelize` prior to 3.35.1 are vulnerable to SQL Injection. The package fails to sanitize JSON path keys in the Postgres dialect,  which may allow attackers to inject SQL statements and execute arbitrary SQL queries.


## Recommendation

Upgrade to version 3.35.1 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10749
- https://github.com/sequelize/sequelize/commit/ee4017379db0059566ecb5424274ad4e2d66bc68
- https://snyk.io/vuln/SNYK-JS-SEQUELIZE-450222
- https://www.npmjs.com/advisories/1017
