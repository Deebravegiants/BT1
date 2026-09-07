# [C] SQL Injection in sequelize

## Summary
Severity: Critical
Advisory: GHSA-j9xp-92vc-559j
CVE: CVE-2019-10748
CWE: CWE-89
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2019-11-06
Source: https://github.com/advisories/GHSA-j9xp-92vc-559j
Type: github-advisory

## Affected
- npm: `sequelize` — affected >=0 <3.35.1
- npm: `sequelize` — affected >=4.0.0 <4.44.3
- npm: `sequelize` — affected >=5.0.0 <5.8.11

## Details
Affected versions of `sequelize` are vulnerable to SQL Injection. The package fails to sanitize JSON path keys in the MariaDB and MySQL dialects,  which may allow attackers to inject SQL statements and execute arbitrary SQL queries.


## Recommendation

If you are using `sequelize` 5.x, upgrade to version 5.8.11 or later.
If you are using `sequelize` 4.x, upgrade to version 4.44.3 or later.
If you are using `sequelize` 3.x, upgrade to version 3.35.1 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10748
- https://github.com/sequelize/sequelize/pull/11089,
- https://github.com/sequelize/sequelize/commit/a72a3f5,
- https://snyk.io/vuln/SNYK-JS-SEQUELIZE-450221
- https://www.npmjs.com/advisories/1018
