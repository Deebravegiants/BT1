# [H] NoSQL Injection in sequelize

## Summary
Severity: High
Advisory: GHSA-wfp9-vr4j-f49j
CWE: CWE-89
Ecosystem: npm
Published: 2019-06-04
Source: https://github.com/advisories/GHSA-wfp9-vr4j-f49j
Type: github-advisory

## Affected
- npm: `sequelize` — affected >=0 <4.12.0

## Details
Versions of `sequelize` prior to 4.12.0 are vulnerable to NoSQL Injection. Query operators such as `$gt` are not properly sanitized and may allow an attacker to alter data queries, leading to NoSQL Injection.


## Recommendation

Upgrade to version 4.12.0 or later

## References
- https://github.com/sequelize/sequelize/issues/7310
- https://github.com/sequelize/sequelize/pull/8240
- https://github.com/sequelize/sequelize/commit/ccb99daedb69e8750a241436415ccac8abef358d
- https://github.com/sequelize/sequelize
- https://snyk.io/vuln/SNYK-JS-SEQUELIZE-174147
