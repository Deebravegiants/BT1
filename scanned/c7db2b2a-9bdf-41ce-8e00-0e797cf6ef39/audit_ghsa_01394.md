# [C] Insufficient Entropy in parsel

## Summary
Severity: Critical
Advisory: GHSA-vjvw-wcmw-pr26
CWE: CWE-331
Ecosystem: npm
Published: 2020-09-04
Source: https://github.com/advisories/GHSA-vjvw-wcmw-pr26
Type: github-advisory

## Affected
- npm: `parsel` — affected >=0.0.0

## Details
All versions of `parsel` use an insecure key derivation function. The package runs keys of arbitrary lengths through one round of SHA256 hashing for key stretching. This allows for the use of keys of insufficient entropy with inappropriate key stretching.


## Recommendation

The package is deprecated and will not be updated. Consider using an alternative package.

## References
- https://www.npmjs.com/advisories/1462
