# [H] Denial of Service in @hapi/content

## Summary
Severity: High
Advisory: GHSA-3wqh-h42r-x8fq
Ecosystem: npm
Published: 2020-09-03
Source: https://github.com/advisories/GHSA-3wqh-h42r-x8fq
Type: github-advisory

## Affected
- npm: `@hapi/content` — affected >=0 <5.0.2

## Details
Versions of `@hapi/content` prior to 4.1.1 and 5.0.1 are vulnerable to Denial of Service. The Content-Encoding HTTP header parser has a vulnerability which will cause the function to throw a system error if the header contains some invalid values. Because hapi rethrows system errors (as opposed to catching expected application errors), the error is thrown all the way up the stack. If no unhandled exception handler is available, the application will exist, allowing an attacker to shut down services.


## Recommendation

Upgrade to version 5.0.2. Versions 4.1.1 and 5.0.1 are fixed but only available for direct download through the repository.

## References
- https://www.npmjs.com/advisories/1476
