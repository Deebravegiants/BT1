# [H] Prototype Pollution in pez

## Summary
Severity: High
Advisory: GHSA-g64q-3vg8-8f93
CWE: CWE-1321
Ecosystem: npm
Published: 2020-09-03
Source: https://github.com/advisories/GHSA-g64q-3vg8-8f93
Type: github-advisory

## Affected
- npm: `pez` — affected >=0.0.0

## Details
All versions of `pez` are vulnerable to Prototype Pollution. A multipart payload can be constructed in a way that one of the parts’ content can be set as the entire payload object’s prototype. If this prototype contains data, it may bypass other validation rules which enforce access and privacy. If this prototype evaluates to null, it can cause unhandled exceptions when the request payload is accessed.


## Recommendation

This package is deprecated and is now maintained as `@hapi/pez`. Please update your dependencies to use `@hapi/pez`.

## References
- https://github.com/hapijs/pez/compare/v4.1.1...v4.1.2
- https://www.npmjs.com/advisories/1479
