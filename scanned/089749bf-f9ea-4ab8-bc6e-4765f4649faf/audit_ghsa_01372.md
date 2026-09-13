# [H] Prototype Pollution in sahmat

## Summary
Severity: High
Advisory: GHSA-83pq-466j-fc6j
CWE: CWE-1321
Ecosystem: npm
Published: 2020-09-04
Source: https://github.com/advisories/GHSA-83pq-466j-fc6j
Type: github-advisory

## Affected
- npm: `sahmat` — affected >=0.0.0

## Details
All versions of `sahmat ` are vulnerable to prototype pollution. The package does not restrict the modification of an Object's prototype, which may allow an attacker to add or modify an existing property that will exist on all objects.




## Recommendation

No fix is currently available. Consider using an alternative package until a fix is made available.

## References
- https://www.npmjs.com/advisories/1336
