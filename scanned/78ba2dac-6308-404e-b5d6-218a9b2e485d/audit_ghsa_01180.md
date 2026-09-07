# [M] Path Traversal in public

## Summary
Severity: Medium
Advisory: GHSA-4vvp-x9h2-x2vf
CWE: CWE-22
Ecosystem: npm
Published: 2020-09-03
Source: https://github.com/advisories/GHSA-4vvp-x9h2-x2vf
Type: github-advisory

## Affected
- npm: `public` — affected >=0.0.0

## Details
All versions of `public` are vulnerable to Path Traversal. This vulnerability allows an attacker to access files outside the webroot since it allows symlink navigation in the URL.


## Recommendation

No fix is currently available. Do not use `public` in production or consider using an alternative module until a fix is made available.

## References
- https://hackerone.com/reports/593911
- https://www.npmjs.com/advisories/1144
