# [M] Out-of-bounds Read in npmconf

## Summary
Severity: Medium
Advisory: GHSA-57cf-349j-352g
CWE: CWE-125
Ecosystem: npm
Published: 2019-06-12
Source: https://github.com/advisories/GHSA-57cf-349j-352g
Type: github-advisory

## Affected
- npm: `npmconf` — affected >=0 <2.1.3

## Details
Versions of `npmconf` before 2.1.3 allocate and write to disk uninitialized memory contents when a typed number is passed as input on Node.js 4.x.


## Recommendation

Update to version 2.1.3 or later. Consider switching to another config storage mechanism, as npmconf is deprecated and should not be used.

## References
- https://hackerone.com/reports/320269
- https://www.npmjs.com/advisories/653
