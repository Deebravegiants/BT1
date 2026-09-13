# [H] Prototype Pollution in safe-object2

## Summary
Severity: High
Advisory: GHSA-qccf-q7p4-3q3j
CWE: CWE-1321
Ecosystem: npm
Published: 2020-09-04
Source: https://github.com/advisories/GHSA-qccf-q7p4-3q3j
Type: github-advisory

## Affected
- npm: `safe-object2` — affected >=0.0.0

## Details
All versions of `safe-object2` are vulnerable to prototype pollution. The `settter()` function does not restrict the modification of an Object's prototype, which may allow an attacker to add or modify an existing property that will exist on all objects.




## Recommendation

No fix is currently available. Consider using an alternative package until a fix is made available.

## References
- https://www.npmjs.com/advisories/1335
