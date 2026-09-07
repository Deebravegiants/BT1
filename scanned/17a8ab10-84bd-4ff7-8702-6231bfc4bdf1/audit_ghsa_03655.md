# [M] Memory Exposure in bl

## Summary
Severity: Medium
Advisory: GHSA-wrw9-m778-g6mc
CWE: CWE-200
Ecosystem: npm
Published: 2019-06-03
Source: https://github.com/advisories/GHSA-wrw9-m778-g6mc
Type: github-advisory

## Affected
- npm: `bl` — affected >=0 <0.9.5
- npm: `bl` — affected >=1.0.0 <1.0.1

## Details
Versions of `bl` before 0.9.5 and 1.0.1 are vulnerable to memory exposure.

`bl.append(number)` in the affected `bl` versions passes a number to Buffer constructor, appending a chunk of uninitialized memory


## Recommendation

Update to version 0.9.5, 1.0.1 or later.

## References
- https://github.com/rvagg/bl/pull/22
- https://www.npmjs.com/advisories/596
