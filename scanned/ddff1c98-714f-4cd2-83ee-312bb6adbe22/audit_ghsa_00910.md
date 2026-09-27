# [C] Command Injection in giting

## Summary
Severity: Critical
Advisory: GHSA-7r9x-hr76-jr96
CWE: CWE-77
Ecosystem: npm
Published: 2020-09-04
Source: https://github.com/advisories/GHSA-7r9x-hr76-jr96
Type: github-advisory

## Affected
- npm: `giting` — affected >=0.0.0

## Details
All versions of `gitting` are vulnerable to Command Injection. The package fails to sanitize input and passes it directly to an `exec` call, which may allow attackers to execute arbitrary code in the system. The `pull` function is vulnerable through the `branch` variable.


## Recommendation

No fix is currently available. Consider using an alternative package until a fix is made available.

## References
- https://www.npmjs.com/advisories/1446
