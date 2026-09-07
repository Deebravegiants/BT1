# [M] Out-of-bounds Read in byte

## Summary
Severity: Medium
Advisory: GHSA-xm7f-x4wx-wmgv
CWE: CWE-125
Ecosystem: npm
Published: 2019-06-04
Source: https://github.com/advisories/GHSA-xm7f-x4wx-wmgv
Type: github-advisory

## Affected
- npm: `byte` — affected >=0 <1.4.1

## Details
Versions of `byte` before 1.4.1 allocate uninitialized buffers and read data from them past the initialized length



## Recommendation

Update to version 1.4.1 or later.

## References
- https://github.com/node-modules/byte/pull/3
- https://hackerone.com/reports/330351
- https://www.npmjs.com/advisories/657
