# [M] Sandbox Breakout / Arbitrary Code Execution in value-censorship

## Summary
Severity: Medium
Advisory: GHSA-xrr6-6ww3-f3qm
Ecosystem: npm
Published: 2020-09-02
Source: https://github.com/advisories/GHSA-xrr6-6ww3-f3qm
Type: github-advisory

## Affected
- npm: `value-censorship` — affected >=0

## Details
All versions of `value-censorship` are vulnerable to Sandbox Escape leading to Remote Code Execution. The package fails to validate async function constructors allowing attackers to execute arbitrary code.


## Recommendation

No fix is currently available. Consider using an alternative package until a fix is made available.

## References
- https://www.npmjs.com/advisories/888
