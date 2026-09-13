# [M] Path Traversal in servey

## Summary
Severity: Medium
Advisory: GHSA-rv49-54qp-fw42
CWE: CWE-22
Ecosystem: npm
Published: 2019-06-06
Source: https://github.com/advisories/GHSA-rv49-54qp-fw42
Type: github-advisory

## Affected
- npm: `servey` — affected >=0 <3.1.0

## Details
Versions of `servey` prior to 3.x are vulnerable to Path Traversal.  Due to insufficient input sanitization, attackers can access server files by using relative paths. 


## Recommendation

Upgrade to the latest version

## References
- https://github.com/typeorm/typeorm/commit/d46c8b0e6c0db56bb5976a4917e9f67a43715111
- https://hackerone.com/reports/355501
- https://www.npmjs.com/advisories/802
