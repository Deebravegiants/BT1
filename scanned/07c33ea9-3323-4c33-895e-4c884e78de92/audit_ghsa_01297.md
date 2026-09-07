# [H] Denial of Service in @hapi/hapi

## Summary
Severity: High
Advisory: GHSA-23vw-mhv5-grv5
Ecosystem: npm
Published: 2020-09-03
Source: https://github.com/advisories/GHSA-23vw-mhv5-grv5
Type: github-advisory

## Affected
- npm: `@hapi/hapi` — affected >=0 <18.4.1
- npm: `@hapi/hapi` — affected >=19.0.0 <19.1.1

## Details
Versions of `@hapi/hapi` prior to 18.4.1 or 19.1.1 are vulnerable to Denial of Service. The CORS request handler has a vulnerability which will cause the function to throw a system error if the header contains some invalid values. If no unhandled exception handler is available, the application will exist, allowing an attacker to shut down services.


## Recommendation

Upgrade to versions 18.4.1, 19.1.1 or later.

## References
- https://www.npmjs.com/advisories/1482
