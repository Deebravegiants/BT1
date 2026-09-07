# [M] Prototype Pollution in smart-extend

## Summary
Severity: Medium
Advisory: GHSA-f8h3-rqrm-47v9
CWE: CWE-1321
Ecosystem: npm
Published: 2020-09-02
Source: https://github.com/advisories/GHSA-f8h3-rqrm-47v9
Type: github-advisory

## Affected
- npm: `smart-extend` — affected >=0

## Details
All versions of `smart-extend` are vulnerable to Prototype Pollution. The `deep()` function allows attackers to modify the prototype of Object causing the addition or modification of an existing property that will exist on all objects.




## Recommendation

No fix is currently available. Consider using an alternative module until a fix is made available.

## References
- https://hackerone.com/reports/438274
- https://www.npmjs.com/advisories/801
