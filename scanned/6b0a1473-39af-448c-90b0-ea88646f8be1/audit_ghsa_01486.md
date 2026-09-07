# [H] Prototype Pollution in flat-wrap

## Summary
Severity: High
Advisory: GHSA-g7h8-p22m-2rvx
CWE: CWE-1321
Ecosystem: npm
Published: 2020-09-04
Source: https://github.com/advisories/GHSA-g7h8-p22m-2rvx
Type: github-advisory

## Affected
- npm: `flat-wrap` — affected >=0.0.0

## Details
All versions of `flat-wrap` are vulnerable to prototype pollution. The function `unflatten` does not restrict the modification of an Object's prototype, which may allow an attacker to add or modify an existing property that will exist on all objects.




## Recommendation

No fix is currently available. Consider using an alternative package until a fix is made available.

## References
- https://www.npmjs.com/advisories/1327
