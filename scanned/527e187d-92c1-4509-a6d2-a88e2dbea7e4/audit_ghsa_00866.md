# [H] Prototype Pollution in get-setter

## Summary
Severity: High
Advisory: GHSA-ch82-gqh6-9xj9
CWE: CWE-1321
Ecosystem: npm
Published: 2020-09-04
Source: https://github.com/advisories/GHSA-ch82-gqh6-9xj9
Type: github-advisory

## Affected
- npm: `get-setter` — affected >=0.0.0

## Details
All versions of `get-setter` are vulnerable to prototype pollution. The function `set` does not restrict the modification of an Object's prototype, which may allow an attacker to add or modify an existing property that will exist on all objects.




## Recommendation

No fix is currently available. Consider using an alternative package until a fix is made available.

## References
- https://www.npmjs.com/advisories/1332
