# [H] Path Traversal in serve

## Summary
Severity: High
Advisory: GHSA-48gc-5j93-5cfq
CWE: CWE-22
Ecosystem: npm
Published: 2020-09-11
Source: https://github.com/advisories/GHSA-48gc-5j93-5cfq
Type: github-advisory

## Affected
- npm: `serve` — affected >=0 <10.1.2

## Details
Versions of `serve` prior to 10.1.2 are vulnerable to Path Traversal. Explicitly ignored folders can be accessed through relative paths, which allows attackers to access hidden folders and files.


## Recommendation

Upgrade to version 10.1.2 or later.

## References
- https://hackerone.com/reports/486933
- https://www.npmjs.com/advisories/965
