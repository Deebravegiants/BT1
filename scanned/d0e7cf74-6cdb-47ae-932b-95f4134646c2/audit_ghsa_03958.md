# [M] Tnantoka/public XSS Vulnerability

## Summary
Severity: Medium
Advisory: GHSA-649c-x44h-4q7v
CVE: CVE-2018-16480
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2019-02-07
Source: https://github.com/advisories/GHSA-649c-x44h-4q7v
Type: github-advisory

## Affected
- npm: `public` — affected >=0 <0.1.4

## Details
A XSS vulnerability was found in module public <0.1.4 that allows malicious Javascript code to run in the browser, due to the absence of sanitization of the file/folder names before rendering.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-16480
- https://hackerone.com/reports/329950
- https://github.com/advisories/GHSA-649c-x44h-4q7v
- https://www.npmjs.com/package/public
