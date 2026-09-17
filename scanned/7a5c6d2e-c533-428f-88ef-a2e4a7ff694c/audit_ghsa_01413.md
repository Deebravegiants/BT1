# [H] Denial of Service in @commercial/hapi

## Summary
Severity: High
Advisory: GHSA-66mv-xh68-h6v2
Ecosystem: npm
Published: 2020-09-03
Source: https://github.com/advisories/GHSA-66mv-xh68-h6v2
Type: github-advisory

## Affected
- npm: `@commercial/hapi` — affected >=0 <16.8.2
- npm: `@commercial/hapi` — affected >=17.0.0 <17.9.2
- npm: `@commercial/hapi` — affected >=18.0.0 <18.4.1
- npm: `@commercial/hapi` — affected >=19.0.0 <19.1.1

## Details
Affected versions of `@commercial/hapi` are vulnerable to Denial of Service. The CORS request handler has a vulnerability which will cause the function to throw a system error if the header contains some invalid values. If no unhandled exception handler is available, the application will exist, allowing an attacker to shut down services.


## Recommendation

Upgrade to versions 16.8.2, 17.9.2, 18.4.1, 19.1.1 or later.

## References
- https://www.npmjs.com/advisories/1483
