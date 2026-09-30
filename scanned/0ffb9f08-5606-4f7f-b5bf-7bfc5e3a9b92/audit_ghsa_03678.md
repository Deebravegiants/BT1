# [M] Memory Exposure in concat-stream

## Summary
Severity: Medium
Advisory: GHSA-g74r-ffvr-5q9f
CWE: CWE-200
Ecosystem: npm
Published: 2019-06-03
Source: https://github.com/advisories/GHSA-g74r-ffvr-5q9f
Type: github-advisory

## Affected
- npm: `concat-stream` — affected >=1.5.0 <1.5.2
- npm: `concat-stream` — affected >=1.4.0 <1.4.11
- npm: `concat-stream` — affected >=1.3.0 <1.3.2

## Details
Versions of `concat-stream` before 1.5.2 are vulnerable to memory exposure if userp provided input is passed into `write()`

Versions <1.3.0 are not affected due to not using unguarded Buffer constructor.



## Recommendation

Update to version 1.5.2, 1.4.11, 1.3.2 or later.

If you are unable to update make sure user provided input into the `write()` function is not a number.

## References
- https://github.com/maxogden/concat-stream/pull/47
- https://github.com/maxogden/concat-stream/pull/47/commits/3e285ba5e5b10b7c98552217f5c1023829efe69e
- https://gist.github.com/ChALkeR/c2d2fd3f1d72d51ad883df195be03a85
- https://www.npmjs.com/advisories/597
