# [M] grapesjs before 0.19.5 vulnerable to Cross-site Scripting

## Summary
Severity: Medium
Advisory: GHSA-589f-c66p-hxr4
CVE: CVE-2022-21802
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-07-26
Source: https://github.com/advisories/GHSA-589f-c66p-hxr4
Type: github-advisory

## Affected
- npm: `grapesjs` — affected >=0

## Details
The package grapesjs before 0.19.5 is vulnerable to Cross-site Scripting (XSS) due to an improper sanitization of the class name in Selector Manager.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-21802
- https://github.com/artf/grapesjs/issues/4411%23issuecomment-1167202709
- https://github.com/artf/grapesjs/commit/13e85d152d486b968265c4b8017e8901e7d89ff3
- https://github.com/artf/grapesjs
- https://github.com/artf/grapesjs/releases/tag/v0.19.5
- https://security.snyk.io/vuln/SNYK-JAVA-ORGWEBJARSNPM-2936781
- https://security.snyk.io/vuln/SNYK-JS-GRAPESJS-2935960
