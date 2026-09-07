# [H] Downloads Resources over HTTP in apk-parser3

## Summary
Severity: High
Advisory: GHSA-4p7j-5ppx-rfhm
CVE: CVE-2016-10574
CWE: CWE-311
Ecosystem: npm
Published: 2020-09-01
Source: https://github.com/advisories/GHSA-4p7j-5ppx-rfhm
Type: github-advisory

## Affected
- npm: `apk-parser3` — affected >=0 <0.1.3

## Details
Affected versions of `apk-parser3` insecurely download an executable over an unencrypted HTTP connection. 

In scenarios where an attacker has a privileged network position, it is possible to intercept the response and replace the executable with a malicious one, resulting in code execution on the system running `apk-parser3`.


## Recommendation

Update to version 0.1.3 or greater.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-10574
- https://www.npmjs.com/advisories/245
