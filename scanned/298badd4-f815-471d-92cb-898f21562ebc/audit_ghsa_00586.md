# [C] Command Injection in apex-publish-static-files

## Summary
Severity: Critical
Advisory: GHSA-9jm3-5835-537m
CVE: CVE-2018-16462
CWE: CWE-77
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2018-11-01
Source: https://github.com/advisories/GHSA-9jm3-5835-537m
Type: github-advisory

## Affected
- npm: `apex-publish-static-files` — affected >=0 <2.0.1

## Details
Versions of `apex-publish-static-files` before 2.0.1 are vulnerable to command injection. This is exploitable if user input is passed into the `connectString` option in the `publish` method.


## Recommendation

Update to version 2.0.1 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-16462
- https://hackerone.com/reports/405694
- https://github.com/advisories/GHSA-9jm3-5835-537m
- https://github.com/nodejs/security-wg/blob/master/vuln/npm/475.json
- https://www.npmjs.com/advisories/718
