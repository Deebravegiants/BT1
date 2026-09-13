# [M] Prototype Pollution in upmerge

## Summary
Severity: Medium
Advisory: GHSA-gm9g-2g8v-fvxj
CWE: CWE-345, CWE-400
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2019-06-06
Source: https://github.com/advisories/GHSA-gm9g-2g8v-fvxj
Type: github-advisory

## Affected
- npm: `upmerge` — affected >=0

## Details
All versions of `upmerge` are vulnerable to Prototype Pollution. The merge() function fails to prevent user input to alter an Object's prototype, allowing attackers to modify override properties of all objects in the application. This may lead to Denial of Service or may be chained with other vulnerabilities leading to Remote Code Execution.


## Recommendation

No fix is currently available. Consider using an alternative module until a fix is made available.

## References
- https://hackerone.com/reports/439120
- https://github.com/jazzfog/UpMerge
- https://snyk.io/vuln/SNYK-JS-UPMERGE-174133
- https://www.npmjs.com/advisories/809
