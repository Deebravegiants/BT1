# [H] Denial of Service in ammo

## Summary
Severity: High
Advisory: GHSA-mg85-8mv5-ffjr
Ecosystem: npm
Published: 2020-09-03
Source: https://github.com/advisories/GHSA-mg85-8mv5-ffjr
Type: github-advisory

## Affected
- npm: `ammo` — affected >=0.0.0

## Details
All versions of `ammo` are vulnerable to Denial of Service. The Range HTTP header parser has a vulnerability which will cause the function to throw a system error if the header is set to an invalid value. Because hapi is not expecting the function to ever throw, the error is thrown all the way up the stack. If no unhandled exception handler is available, the application will exist, allowing an attacker to shut down services.


## Recommendation

This package is deprecated and is now maintained as `@hapi/ammo`. Please update your dependencies to use `@hapi/ammo`.

## References
- https://www.npmjs.com/advisories/1472
