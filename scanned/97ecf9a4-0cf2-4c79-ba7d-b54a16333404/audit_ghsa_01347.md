# [H] NoSQL Injection in loopback-connector-mongodb

## Summary
Severity: High
Advisory: GHSA-hxwc-5vw9-2w4w
CWE: CWE-89
Ecosystem: npm
Published: 2020-09-02
Source: https://github.com/advisories/GHSA-hxwc-5vw9-2w4w
Type: github-advisory

## Affected
- npm: `loopback-connector-mongodb` — affected >=0 <3.6.0

## Details
Versions of `loopback-connector-mongodb` prior to 3.6.0 are vulnerable to NoSQL Injection. Filters passed to the database query are not properly sanitized which leads to execution of code on the database driver and data leak.


## Recommendation

Upgrade to version 3.6.0 or later.

## References
- https://github.com/loopbackio/loopback-connector-mongodb
- https://loopback.io/doc/en/lb3/Security-advisory-08-15-2018.html
- https://www.npmjs.com/advisories/767
