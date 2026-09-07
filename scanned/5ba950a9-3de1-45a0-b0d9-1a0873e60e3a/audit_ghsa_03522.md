# [M] Docsify XSS Vulnerability

## Summary
Severity: Medium
Advisory: GHSA-2mm9-c2fx-c7m4
CVE: CVE-2021-23342
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2021-03-01
Source: https://github.com/advisories/GHSA-2mm9-c2fx-c7m4
Type: github-advisory

## Affected
- npm: `docsify` — affected >=0 <4.12.0

## Details
This affects the package docsify before 4.12.0. It is possible to bypass the remediation done by CVE-2020-7680 and execute malicious JavaScript through the following methods 1) When parsing HTML from remote URLs, the HTML code on the main page is sanitized, but this sanitization is not taking place in the sidebar. 2) The isURL external check can be bypassed by inserting more `////` characters

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-23342
- https://github.com/docsifyjs/docsify/commit/ff2a66f12752471277fe81a64ad6c4b2c08111fe
- https://snyk.io/vuln/SNYK-JAVA-ORGWEBJARSNPM-1076593
- https://snyk.io/vuln/SNYK-JS-DOCSIFY-1066017
- https://www.npmjs.com/package/docsify
- http://packetstormsecurity.com/files/161495/docsify-4.11.6-Cross-Site-Scripting.html
- http://seclists.org/fulldisclosure/2021/Feb/71
