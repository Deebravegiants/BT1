# [H] Prototype Pollution in unflatten

## Summary
Severity: High
Advisory: GHSA-6fh5-8wq8-w3wr
CWE: CWE-1321
Ecosystem: npm
Published: 2020-09-04
Source: https://github.com/advisories/GHSA-6fh5-8wq8-w3wr
Type: github-advisory

## Affected
- npm: `unflatten` — affected >=0.0.0

## Details
All versions of `unflatten` are vulnerable to prototype pollution. The function `unflatten` does not restrict the modification of an Object's prototype, which may allow an attacker to add or modify an existing property that will exist on all objects.




## Recommendation

No fix is currently available. Consider using an alternative package until a fix is made available.

## References
- https://www.npmjs.com/advisories/1329
