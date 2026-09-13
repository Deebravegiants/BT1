# [M] SQL Injection in sequelize

## Summary
Severity: Medium
Advisory: GHSA-x2jc-pwfj-h9p3
CVE: CVE-2016-10554
CWE: CWE-89
Ecosystem: npm
Published: 2019-02-18
Source: https://github.com/advisories/GHSA-x2jc-pwfj-h9p3
Type: github-advisory

## Affected
- npm: `sequelize` — affected >=0 <1.7.0

## Details
Affected versions of `sequelize` use MySQL's backslash-based escape syntax when connecting to SQLite, despite the fact that SQLite uses PostgreSQL's escape syntax, which can result in a SQL Injection vulnerability.


## Recommendation

Update to version 1.7.0-alpha3 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-10554
- https://github.com/sequelize/sequelize/commit/c876192aa6ce1f67e22b26a4d175b8478615f42d
- https://github.com/advisories/GHSA-x2jc-pwfj-h9p3
- https://www.npmjs.com/advisories/113
