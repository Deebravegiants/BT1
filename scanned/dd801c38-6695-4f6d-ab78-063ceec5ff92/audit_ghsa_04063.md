# [M] Out-of-bounds Read in concat-with-sourcemaps

## Summary
Severity: Medium
Advisory: GHSA-2xv3-h762-ccxv
CWE: CWE-125
Ecosystem: npm
Published: 2019-05-29
Source: https://github.com/advisories/GHSA-2xv3-h762-ccxv
Type: github-advisory

## Affected
- npm: `concat-with-sourcemaps` — affected >=1.0.0 <1.0.6

## Details
Versions of `concat-with-sourcemaps` before 1.0.6 allocates uninitialized Buffers when a number is passed as a separator.


## Recommendation

Update to version 1.0.6 or later.

## References
- https://hackerone.com/reports/320166
- https://github.com/floridoo/concat-with-sourcemaps/blob/v1.0.5/index.js#L18
- https://www.npmjs.com/advisories/644
