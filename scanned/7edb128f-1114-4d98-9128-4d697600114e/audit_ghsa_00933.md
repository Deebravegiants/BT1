# [C] Command Injection in priest-runner

## Summary
Severity: Critical
Advisory: GHSA-9px9-f7jw-fwhj
CWE: CWE-77
Ecosystem: npm
Published: 2020-09-03
Source: https://github.com/advisories/GHSA-9px9-f7jw-fwhj
Type: github-advisory

## Affected
- npm: `priest-runner` — affected >=0.0.0

## Details
All versions of `priest-runner` are vulnerable to Command Injection. The package fails to sanitize input and passes it directly to a `spawn` call, which may allow attackers to execute arbitrary code in the system. The `PriestController.prototype.createChild ` function is vulnerable since the `spawn` parameters come from a POST request body.


## Recommendation

No fix is currently available. Consider using an alternative package until a fix is made available.

## References
- https://www.npmjs.com/advisories/1492
