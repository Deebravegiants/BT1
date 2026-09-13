# [H] Denial of Service in @commercial/subtext

## Summary
Severity: High
Advisory: GHSA-cvfm-xjc8-f2vm
Ecosystem: npm
Published: 2020-09-03
Source: https://github.com/advisories/GHSA-cvfm-xjc8-f2vm
Type: github-advisory

## Affected
- npm: `@commercial/subtext` — affected >=5.1.1 <5.1.2

## Details
Version 5.1.1 of `@commercial/subtext` is vulnerable to Denial of Service. The Content-Encoding HTTP header parser has a vulnerability which will cause the function to throw a system error if the header contains some invalid values. Because hapi rethrows system errors (as opposed to catching expected application errors), the error is thrown all the way up the stack. If no unhandled exception handler is available, the application will exist, allowing an attacker to shut down services.


## Recommendation

Upgrade to version 5.1.2 or later.

## References
- https://www.npmjs.com/advisories/1477
