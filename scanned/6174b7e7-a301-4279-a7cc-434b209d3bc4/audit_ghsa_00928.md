# [C] Sandbox Breakout / Arbitrary Code Execution in lighter-vm

## Summary
Severity: Critical
Advisory: GHSA-c3hq-7mxh-mqxf
Ecosystem: npm
Published: 2020-09-04
Source: https://github.com/advisories/GHSA-c3hq-7mxh-mqxf
Type: github-advisory

## Affected
- npm: `lighter-vm` — affected >=0.0.0

## Details
All versions of `lighter-vm` are vulnerable to Sandbox Escape leading to Remote Code Execution. The package fails to restrict access to the main context through `this.constructor.constructor` . This may allow attackers to execute arbitrary code in the system. Evaluating the payload `this.constructor.constructor('return process.env')()` prints the contents of `process.env`.


## Recommendation

No fix is currently available. Consider using an alternative package until a fix is made available.

## References
- https://www.npmjs.com/advisories/1317
