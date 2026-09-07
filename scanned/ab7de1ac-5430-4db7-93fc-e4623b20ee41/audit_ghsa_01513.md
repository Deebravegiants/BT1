# [C] Insecure Cryptography Algorithm in parsel

## Summary
Severity: Critical
Advisory: GHSA-wqgx-4q47-j2w5
CWE: CWE-327
Ecosystem: npm
Published: 2020-09-04
Source: https://github.com/advisories/GHSA-wqgx-4q47-j2w5
Type: github-advisory

## Affected
- npm: `parsel` — affected >=0.0.0

## Details
All versions of `parsel` use an insecure cryptography algorithm. The package uses `aes-256-cbc` without integrity checks, which renders the ciphertext vulnerable to bit-flipping attacks.


## Recommendation

The package is deprecated and will not be updated. Consider using an alternative package.

## References
- https://www.npmjs.com/advisories/1461
