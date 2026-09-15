# [C] Path Traversal in swagger-injector

## Summary
Severity: Critical
Advisory: GHSA-v4x8-gw49-7hv4
CWE: CWE-22
Ecosystem: npm
Published: 2020-09-03
Source: https://github.com/advisories/GHSA-v4x8-gw49-7hv4
Type: github-advisory

## Affected
- npm: `swagger-injector` — affected >=0.0.0

## Details
All versions of `swagger-injector` are vulnerable to Path Traversal. The package fails to sanitize URLs, allowing attackers to access server files outside of the configured `dist` folder using relative paths.


## Recommendation

No fix is currently available. Consider using an alternative package until a fix is made available.

## References
- https://www.npmjs.com/advisories/1172
