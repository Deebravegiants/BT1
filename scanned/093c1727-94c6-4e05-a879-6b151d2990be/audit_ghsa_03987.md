# [H] SQL Injection in sequelize

## Summary
Severity: High
Advisory: GHSA-98pq-pmw9-4gpm
CVE: CVE-2016-10550
CWE: CWE-89
Ecosystem: npm
Published: 2019-02-18
Source: https://github.com/advisories/GHSA-98pq-pmw9-4gpm
Type: github-advisory

## Affected
- npm: `sequelize` — affected >=0 <3.17.0

## Details
Affected versions of `sequelize` are vulnerable to SQL Injection in locations where user input is passed into the `limit` or `order` parameters of `sequelize` query calls, such as `findOne` or `findAll`.



## Recommendation

Update to version 3.17.0 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-10550
- https://github.com/sequelize/sequelize/pull/5167/commits/f282d85e60e3df5e57ecdb82adccb4eaef404f03
- https://github.com/advisories/GHSA-98pq-pmw9-4gpm
- https://www.npmjs.com/advisories/112
