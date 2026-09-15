# [H] Prototype Pollution in lodash.merge

## Summary
Severity: High
Advisory: GHSA-2m96-9w4j-wgv7
CWE: CWE-1321
Ecosystem: npm
Published: 2020-09-03
Source: https://github.com/advisories/GHSA-2m96-9w4j-wgv7
Type: github-advisory

## Affected
- npm: `lodash.merge` — affected >=0 <4.6.1

## Details
Versions of `lodash.merge` before 4.6.1 are vulnerable to Prototype Pollution. The function 'merge' may allow a malicious user to modify the prototype of `Object` via `__proto__` causing the addition or modification of an existing property that will exist on all objects.




## Recommendation

Update to version 4.6.1 or later.

## References
- https://www.npmjs.com/advisories/1067
