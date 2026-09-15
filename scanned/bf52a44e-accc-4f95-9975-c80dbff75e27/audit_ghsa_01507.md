# [H] Path Traversal in bruteser

## Summary
Severity: High
Advisory: GHSA-v7cp-5326-54fh
CWE: CWE-22
Ecosystem: npm
Published: 2020-09-03
Source: https://github.com/advisories/GHSA-v7cp-5326-54fh
Type: github-advisory

## Affected
- npm: `bruteser` — affected >=0 <0.1.0

## Details
Versions of `bruteser` prior to 0.1.0 are vulnerable to Path Traversal. The package fails to sanitize URLs, allowing attackers to access server files outside of the served folder using relative paths.


## Recommendation

Upgrade to version 0.1.0 or later.

## References
- https://hackerone.com/reports/342066
- https://www.npmjs.com/advisories/999
