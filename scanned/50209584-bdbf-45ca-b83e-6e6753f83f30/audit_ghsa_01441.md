# [C] Command Injection in npm-git-publish

## Summary
Severity: Critical
Advisory: GHSA-49mg-94fc-2fx6
CWE: CWE-77
Ecosystem: npm
Published: 2020-09-04
Source: https://github.com/advisories/GHSA-49mg-94fc-2fx6
Type: github-advisory

## Affected
- npm: `npm-git-publish` — affected >=0.0.0

## Details
All versions of `npm-git-publish` are vulnerable to Command Injection. The package fails to sanitize input and passes it directly to an `execSync` call, which may allow attackers to execute arbitrary code in the system. The `publish` function is vulnerable through the `gitRemoteUrl` variable.


## Recommendation

No fix is currently available. Consider using an alternative package until a fix is made available.

## References
- https://hackerone.com/reports/730121
- https://www.npmjs.com/advisories/1458
