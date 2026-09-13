# [H] Path Traversal in zero

## Summary
Severity: High
Advisory: GHSA-crf7-fvjx-863q
CWE: CWE-22
Ecosystem: npm
Published: 2020-09-03
Source: https://github.com/advisories/GHSA-crf7-fvjx-863q
Type: github-advisory

## Affected
- npm: `zero` — affected >=0 <1.0.6

## Details
Versions of `zero` prior to 1.0.6 are vulnerable to Path Traversal.  Due to insufficient input sanitization in URLs, attackers can access server files by using relative paths when fetching files. 


## Recommendation

Upgrade to version 1.0.6 or later.

## References
- https://www.npmjs.com/advisories/1025
