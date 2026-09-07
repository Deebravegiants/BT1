# [M] Prototype Pollution in mergify

## Summary
Severity: Medium
Advisory: GHSA-3f95-w5h5-fq86
CWE: CWE-1321
Ecosystem: npm
Published: 2020-09-11
Source: https://github.com/advisories/GHSA-3f95-w5h5-fq86
Type: github-advisory

## Affected
- npm: `mergify` — affected >=0

## Details
All versions of `mergify` are vulnerable to Prototype Pollution. The `mergify()` function allows attackers to modify the prototype of Object causing the addition or modification of an existing property that will exist on all objects.




## Recommendation

No fix is currently available. Consider using an alternative module as the package is deprecated.

## References
- https://hackerone.com/reports/439098
- https://www.npmjs.com/advisories/995
