# [M] Command Injection in wxchangba

## Summary
Severity: Medium
Advisory: GHSA-j6v9-xgvh-f796
CWE: CWE-77
Ecosystem: npm
Published: 2020-09-11
Source: https://github.com/advisories/GHSA-j6v9-xgvh-f796
Type: github-advisory

## Affected
- npm: `wxchangba` — affected >=0.0.0

## Details
All versions of `wxchangba` are vulnerable to Command Injection. The package does not validate user input on the `reqPostMaterial` function, passing contents of the `file` parameter to an exec call. This may allow attackers to run arbitrary commands in the system.


## Recommendation

No fix is currently available. Consider using an alternative module until a fix is made available.

## References
- https://www.npmjs.com/advisories/960
