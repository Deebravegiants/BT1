# [H] Denial of Service in mongodb

## Summary
Severity: High
Advisory: GHSA-mh5c-679w-hh4r
Ecosystem: npm
Published: 2020-09-03
Source: https://github.com/advisories/GHSA-mh5c-679w-hh4r
Type: github-advisory

## Affected
- npm: `mongodb` — affected >=0 <3.1.13

## Details
Versions of `mongodb` prior to 3.1.13 are vulnerable to Denial of Service. The package fails to properly catch an exception when a collection name is invalid and the DB does not exist, crashing the application.


## Recommendation

Upgrade to version 3.1.13 or later.

## References
- https://www.npmjs.com/advisories/1203
