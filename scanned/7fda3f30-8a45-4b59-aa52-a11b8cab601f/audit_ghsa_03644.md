# [M] Out-of-bounds Read in stringstream

## Summary
Severity: Medium
Advisory: GHSA-mf6x-7mm4-x2g7
CVE: CVE-2018-21270
CWE: CWE-125
Ecosystem: npm
Published: 2019-06-20
Source: https://github.com/advisories/GHSA-mf6x-7mm4-x2g7
Type: github-advisory

## Affected
- npm: `stringstream` — affected >=0 <0.0.6

## Details
All versions of `stringstream` are vulnerable to out-of-bounds read as it allocates uninitialized Buffers when number is passed in input stream on Node.js 4.x and below.


## Recommendation

No fix is currently available for this vulnerability. It is our recommendation to not install or use this module if user input is being passed in to `stringstream`.

## References
- https://hackerone.com/reports/321670
- https://github.com/mhart/StringStream/blob/v0.0.5/stringstream.js#L32
- https://www.npmjs.com/advisories/664
