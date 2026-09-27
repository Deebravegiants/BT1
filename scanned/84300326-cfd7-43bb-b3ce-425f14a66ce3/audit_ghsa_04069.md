# [H] Out-of-bounds Read in base64-url

## Summary
Severity: High
Advisory: GHSA-j4mr-9xw3-c9jx
CWE: CWE-125
Ecosystem: npm
Published: 2019-05-31
Source: https://github.com/advisories/GHSA-j4mr-9xw3-c9jx
Type: github-advisory

## Affected
- npm: `base64-url` — affected >=0 <2.0.0

## Details
Versions of `base64-url` before 2.0.0 are vulnerable to out-of-bounds read as it allocates uninitialized Buffers when number is passed in input.


## Recommendation

Update to version 2.0.0 or later.

## References
- https://hackerone.com/reports/321692
- https://www.npmjs.com/advisories/660
