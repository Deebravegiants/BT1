# [M] Sandbox Breakout / Prototype Pollution in notevil

## Summary
Severity: Medium
Advisory: GHSA-9gxr-rhx6-4jgv
CWE: CWE-1321
Ecosystem: npm
Published: 2020-09-04
Source: https://github.com/advisories/GHSA-9gxr-rhx6-4jgv
Type: github-advisory

## Affected
- npm: `notevil` — affected >=0 <1.3.3

## Details
Versions of `notevil` prior to 1.3.3 are vulnerable to Sandbox Escape leading to Prototype pollution. The package fails to restrict access to the main context, allowing attacker to add or modify an object's prototype.

Evaluating the payload ```try{a[b];}catch(e){e.constructor.constructor('return __proto__.arguments.callee.__proto__.polluted=true')()}``` add the `polluted` property to Function.


## Recommendation

Upgrade to version 1.3.3 or later.

## References
- https://www.npmjs.com/advisories/1338
