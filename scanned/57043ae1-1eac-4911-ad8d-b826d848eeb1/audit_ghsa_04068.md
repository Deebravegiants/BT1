# [M] Cryptographically Weak PRNG in generate-password

## Summary
Severity: Medium
Advisory: GHSA-6qqf-vvcr-7qrv
CWE: CWE-338
Ecosystem: npm
Published: 2019-05-23
Source: https://github.com/advisories/GHSA-6qqf-vvcr-7qrv
Type: github-advisory

## Affected
- npm: `generate-password` — affected >=0 <1.4.1

## Details
Affected versions of generate-password generate random values that are biased towards certain characters depending on the chosen character sets. This may result in guessable passwords.


## Recommendation

Update to version 1.4.1 or later.

## References
- https://github.com/brendanashworth/generate-password/pull/26
- https://www.npmjs.com/advisories/762
