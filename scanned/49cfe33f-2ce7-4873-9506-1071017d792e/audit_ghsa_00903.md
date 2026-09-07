# [H] Path Traversal in file-static-server

## Summary
Severity: High
Advisory: GHSA-qjfh-xc44-rm9x
CWE: CWE-22
Ecosystem: npm
Published: 2020-09-03
Source: https://github.com/advisories/GHSA-qjfh-xc44-rm9x
Type: github-advisory

## Affected
- npm: `file-static-server` — affected >=0.0.0

## Details
All versions of `file-static-server` are vulnerable to Path Traversal.  Due to insufficient input sanitization in URLs, attackers can access server files by using relative paths when fetching files. 


## Recommendation

No fix is currently available. Consider using an alternative module until a fix is made available.

## References
- https://hackerone.com/reports/310671
- https://www.npmjs.com/advisories/1008
