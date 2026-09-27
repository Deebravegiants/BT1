# [H] Hardcoded Initialization Vector in parsel

## Summary
Severity: High
Advisory: GHSA-q643-w9jp-q2qg
Ecosystem: npm
Published: 2020-09-04
Source: https://github.com/advisories/GHSA-q643-w9jp-q2qg
Type: github-advisory

## Affected
- npm: `parsel` — affected >=0.0.0

## Details
All versions of `parsel` have a default hardcoded initialization vector. In cases where the IV is not provided, the package defaults to a hardcoded IV which renders the cipher vulnerable to chosen plaintext attacks.


## Recommendation

The package is deprecated and will not be updated. Consider using an alternative package.

## References
- https://www.npmjs.com/advisories/1460
