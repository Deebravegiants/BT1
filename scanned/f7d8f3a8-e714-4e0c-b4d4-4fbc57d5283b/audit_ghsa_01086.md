# [H] Denial of Service in @hapi/ammo

## Summary
Severity: High
Advisory: GHSA-gjph-xf5q-6mfq
Ecosystem: npm
Published: 2020-09-03
Source: https://github.com/advisories/GHSA-gjph-xf5q-6mfq
Type: github-advisory

## Affected
- npm: `@hapi/ammo` — affected >=0 <3.1.2
- npm: `@hapi/ammo` — affected >=4.0.0 <5.0.1

## Details
Versions of `@hapi/ammo` prior to 3.1.2 or 5.0.1 are vulnerable to Denial of Service. The Range HTTP header parser has a vulnerability which will cause the function to throw a system error if the header is set to an invalid value. Because hapi is not expecting the function to ever throw, the error is thrown all the way up the stack. If no unhandled exception handler is available, the application will exist, allowing an attacker to shut down services.


## Recommendation

Upgrade to version 3.1.2 or 5.0.1.

## References
- https://www.npmjs.com/advisories/1474
