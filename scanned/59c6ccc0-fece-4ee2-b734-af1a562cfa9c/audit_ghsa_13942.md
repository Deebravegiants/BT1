# [M] textAngular Cross-site Scripting vulnerability

## Summary
Severity: Medium
Advisory: GHSA-7h4w-6p98-r3wx
CVE: CVE-2021-32854
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2023-02-21
Source: https://github.com/advisories/GHSA-7h4w-6p98-r3wx
Type: github-advisory

## Affected
- npm: `textangular` — affected >=0

## Details
textAngular is a text editor for Angular.js. Version 1.5.16 and prior are vulnerable to copy-paste cross-site scripting (XSS). For this particular type of XSS, the victim needs to be fooled into copying a malicious payload into the text editor. There are no known patches.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-32854
- https://github.com/textAngular/textAngular
- https://securitylab.github.com/advisories/GHSL-2021-1001-textAngular
