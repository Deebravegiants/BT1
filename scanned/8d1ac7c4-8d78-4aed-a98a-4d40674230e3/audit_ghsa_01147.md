# [H] Prototype Pollution in lodash.defaultsdeep

## Summary
Severity: High
Advisory: GHSA-46fh-8fc5-xcwx
CWE: CWE-1321
Ecosystem: npm
Published: 2020-09-03
Source: https://github.com/advisories/GHSA-46fh-8fc5-xcwx
Type: github-advisory

## Affected
- npm: `lodash.defaultsdeep` — affected >=0 <4.6.1

## Details
Versions of `lodash.defaultsdeep` before 4.6.1 are vulnerable to Prototype Pollution. The function 'defaultsDeep' may allow a malicious user to modify the prototype of `Object` via `__proto__` causing the addition or modification of an existing property that will exist on all objects.




## Recommendation

Update to version 4.6.1 or later.

## References
- https://www.npmjs.com/advisories/1070
