# [H] Prototype Pollution in getsetdeep

## Summary
Severity: High
Advisory: GHSA-8j49-49jq-vwcq
CWE: CWE-1321
Ecosystem: npm
Published: 2020-09-04
Source: https://github.com/advisories/GHSA-8j49-49jq-vwcq
Type: github-advisory

## Affected
- npm: `getsetdeep` — affected >=0.0.0

## Details
All versions of `getsetdeep` are vulnerable to prototype pollution. The `setDeep()` function does not restrict the modification of an Object's prototype, which may allow an attacker to add or modify an existing property that will exist on all objects.




## Recommendation

No fix is currently available. Consider using an alternative package until a fix is made available.

## References
- https://www.npmjs.com/advisories/1334
