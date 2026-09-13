# [M] Prototype Pollution in lutils-merge

## Summary
Severity: Medium
Advisory: GHSA-f7qw-5pvg-mmwp
CWE: CWE-400
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2019-06-13
Source: https://github.com/advisories/GHSA-f7qw-5pvg-mmwp
Type: github-advisory

## Affected
- npm: `lutils-merge` — affected >=0

## Details
All versions of `lutils-merge` are vulnerable to Prototype Pollution. The merge() function fails to prevent user input to alter an Object's prototype, allowing attackers to modify override properties of all objects in the application. This may lead to Denial of Service or may be chained with other vulnerabilities leading to Remote Code Execution.


## Recommendation

The package is deprecated and no fixes are available. Consider using an alternative package.

## References
- https://github.com/nfour/lutils-merge/issues/1
- https://hackerone.com/reports/439107
- https://snyk.io/vuln/SNYK-JS-LUTILSMERGE-174783
- https://www.npmjs.com/advisories/893
