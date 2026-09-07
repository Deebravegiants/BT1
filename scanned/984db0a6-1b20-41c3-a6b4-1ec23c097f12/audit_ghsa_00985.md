# [H] Denial of Service in content

## Summary
Severity: High
Advisory: GHSA-5854-jvxx-2cg9
Ecosystem: npm
Published: 2020-09-03
Source: https://github.com/advisories/GHSA-5854-jvxx-2cg9
Type: github-advisory

## Affected
- npm: `content` — affected >=0

## Details
Versions of `content` are vulnerable to Denial of Service. The Content-Encoding HTTP header parser has a vulnerability which will cause the function to throw a system error if the header contains some invalid values. Because hapi rethrows system errors (as opposed to catching expected application errors), the error is thrown all the way up the stack. If no unhandled exception handler is available, the application will exist, allowing an attacker to shut down services.

## Recommendation

This package is deprecated and is now maintained as `@hapi/content`. Please update your dependencies to use `@hapi/content`.

## References
- https://github.com/hapijs/content/compare/v4.1.0...v4.1.1
- https://github.com/hapijs/subtext
- https://www.npmjs.com/advisories/1478
