# [M] Out-of-bounds Read in base64url

## Summary
Severity: Medium
Advisory: GHSA-rvg8-pwq2-xj7q
CWE: CWE-125
Ecosystem: npm
Published: 2020-09-01
Source: https://github.com/advisories/GHSA-rvg8-pwq2-xj7q
Type: github-advisory

## Affected
- npm: `base64url` — affected >=0 <3.0.0

## Details
Versions of `base64url` before 3.0.0 are vulnerable to to out-of-bounds reads as it allocates uninitialized Buffers when number is passed in input on Node.js 4.x and below.


## Recommendation

Update to version 3.0.0 or later.

## References
- https://github.com/brianloveswords/base64url/pull/25
- https://github.com/brianloveswords/base64url/commit/4fbd954a0a69e9d898de2146557cc6e893e79542
- https://hackerone.com/reports/321687
- https://github.com/brianloveswords/base64url
