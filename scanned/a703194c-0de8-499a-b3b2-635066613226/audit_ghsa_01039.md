# [H] Path Traversal in restify-swagger-jsdoc

## Summary
Severity: High
Advisory: GHSA-gvff-25cc-4f66
CWE: CWE-22
Ecosystem: npm
Published: 2020-09-03
Source: https://github.com/advisories/GHSA-gvff-25cc-4f66
Type: github-advisory

## Affected
- npm: `restify-swagger-jsdoc` — affected >=0 <3.2.1

## Details
Versions of `restify-swagger-jsdoc` prior to 3.2.1 are vulnerable to Path Traversal.  The package fails to properly sanitize URLs, which may allow attackers to access server files outside the `swagger-ui` folder by using relative paths.  



## Recommendation

Upgrade to version 3.2.1 or later.

## References
- https://www.npmjs.com/advisories/1037
