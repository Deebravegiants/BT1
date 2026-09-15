# [C] Path Traversal in f-serv

## Summary
Severity: Critical
Advisory: GHSA-vx5w-cxch-wwc9
CWE: CWE-22
Ecosystem: npm
Published: 2020-09-03
Source: https://github.com/advisories/GHSA-vx5w-cxch-wwc9
Type: github-advisory

## Affected
- npm: `f-serv` — affected >=0.0.0

## Details
All versions of `f-serv` are vulnerable to Path Traversal.  Due to insufficient input sanitization in URLs, attackers can access server files by using relative paths when fetching files. 


## Recommendation

No fix is currently available. Consider using an alternative package until a fix is made available.

## References
- https://www.npmjs.com/advisories/1092
