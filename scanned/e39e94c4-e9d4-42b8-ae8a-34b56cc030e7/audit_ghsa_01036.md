# [C] Command Injection in meta-git

## Summary
Severity: Critical
Advisory: GHSA-qcff-ffx3-m25c
CWE: CWE-77
Ecosystem: npm
Published: 2020-09-04
Source: https://github.com/advisories/GHSA-qcff-ffx3-m25c
Type: github-advisory

## Affected
- npm: `meta-git` — affected >=0.0.0

## Details
All versions of `meta-git` are vulnerable to Command Injection. The package fails to sanitize input and passes it directly to an `exec` call, which may allow attackers to execute arbitrary code in the system. The `clone` command is vulnerable through the branch name.


## Recommendation

No fix is currently available. Consider using an alternative package until a fix is made available.

## References
- https://hackerone.com/reports/728040
- https://www.npmjs.com/advisories/1457
