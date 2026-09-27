# [H] Command Injection in tomato

## Summary
Severity: High
Advisory: GHSA-wqhw-frpx-5mmp
CWE: CWE-77
Ecosystem: npm
Published: 2020-09-02
Source: https://github.com/advisories/GHSA-wqhw-frpx-5mmp
Type: github-advisory

## Affected
- npm: `tomato` — affected >=0

## Details
All versions of `tomato` are vulnerable to Command Injection. The /api/exec endpoint does not validate user input allowing attackers to run arbitrary commands in the system.


## Recommendation

No fix is currently available. Consider using an alternative module until a fix is made available.

## References
- https://www.npmjs.com/advisories/797
