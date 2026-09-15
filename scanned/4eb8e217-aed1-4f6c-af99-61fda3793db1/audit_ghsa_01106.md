# [C] Sandbox Breakout / Arbitrary Code Execution in localeval

## Summary
Severity: Critical
Advisory: GHSA-mmqv-m45h-q2hp
Ecosystem: npm
Published: 2020-09-04
Source: https://github.com/advisories/GHSA-mmqv-m45h-q2hp
Type: github-advisory

## Affected
- npm: `localeval` — affected >=0 <15.3.0

## Details
All versions of `localeval` are vulnerable to Sandbox Escape leading to Remote Code Execution. The package fails to restrict access to the main context through `constructor.constructor`. This may allow attackers to execute arbitrary code in the system.  Evaluating the payload 
```
constructor.constructor("return process.env")()
``` 

returns the contents of `process.env`.


## Recommendation

No fix is currently available. Consider using an alternative package until a fix is made available.

## References
- https://github.com/espadrine/localeval/issues/9
- https://github.com/espadrine/localeval/commit/823f112c793b8fae051eeddad61d4ed29804a56c
- https://github.com/espadrine/localeval/commit/ce985eba77a5f89a7f718727cbaa7fb14da40335
- https://github.com/espadrine/localeval
