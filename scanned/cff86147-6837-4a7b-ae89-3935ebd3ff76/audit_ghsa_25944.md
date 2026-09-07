# [H] Code injection in accesslog

## Summary
Severity: High
Advisory: GHSA-8m2f-74r2-x3f2
CVE: CVE-2022-25760
CWE: CWE-94
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:L (CVSS_V3)
Published: 2022-03-18
Source: https://github.com/advisories/GHSA-8m2f-74r2-x3f2
Type: github-advisory

## Affected
- npm: `accesslog` — affected >=0

## Details
All versions of package accesslog are vulnerable to Arbitrary Code Injection due to the usage of the Function constructor without input sanitization. If (attacker-controlled) user input is given to the format option of the package's exported constructor function, it is possible for an attacker to execute arbitrary JavaScript code on the host that this package is being run on.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-25760
- https://github.com/carlos8f/node-accesslog
- https://github.com/carlos8f/node-accesslog/blob/master/lib/compile.js%23L6
- https://snyk.io/vuln/SNYK-JS-ACCESSLOG-2312099
