# [H] Denial of Service in hapi

## Summary
Severity: High
Advisory: GHSA-7hx8-2rxv-66xv
Ecosystem: npm
Published: 2020-09-03
Source: https://github.com/advisories/GHSA-7hx8-2rxv-66xv
Type: github-advisory

## Affected
- npm: `hapi` — affected >=0.0.0

## Details
All Versions of `hapi` are vulnerable to Denial of Service. The CORS request handler has a vulnerability which will cause the function to throw a system error if the header contains some invalid values. If no unhandled exception handler is available, the application will exist, allowing an attacker to shut down services.


## Recommendation

This package is deprecated and is now maintained as `@hapi/hapi`. Please update your dependencies to use `@hapi/hapi`.

## References
- https://www.npmjs.com/advisories/1481
