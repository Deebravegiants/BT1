# [H] Denial of Service in @commercial/ammo

## Summary
Severity: High
Advisory: GHSA-rhc3-76jw-4f2x
Ecosystem: npm
Published: 2020-09-04
Source: https://github.com/advisories/GHSA-rhc3-76jw-4f2x
Type: github-advisory

## Affected
- npm: `@commercial/ammo` — affected >=0 <2.1.1

## Details
Versions of `@commercial/ammo` prior to 2.1.1 are vulnerable to Denial of Service. The Range HTTP header parser has a vulnerability which will cause the function to throw a system error if the header is set to an invalid value. Because hapi is not expecting the function to ever throw, the error is thrown all the way up the stack. If no unhandled exception handler is available, the application will exist, allowing an attacker to shut down services.


## Recommendation

Upgrade to version 2.1.1 or later.

## References
- https://www.npmjs.com/advisories/1473
