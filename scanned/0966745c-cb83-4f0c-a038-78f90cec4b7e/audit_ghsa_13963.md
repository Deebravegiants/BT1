# [M] Vditor Cross-site Scripting vulnerability

## Summary
Severity: Medium
Advisory: GHSA-vfmp-9999-6wqj
CVE: CVE-2021-32855
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2023-02-21
Source: https://github.com/advisories/GHSA-vfmp-9999-6wqj
Type: github-advisory

## Affected
- npm: `vditor` — affected >=0 <3.8.7

## Details
Vditor is a browser-side Markdown editor. Versions prior to 3.8.7 are vulnerable to copy-paste cross-site scripting (XSS). For this particular type of XSS, the victim needs to be fooled into copying a malicious payload into the text editor. Version 3.8.7 contains a patch for this issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-32855
- https://github.com/Vanessa219/vditor/issues/1085
- https://github.com/Vanessa219/vditor/commit/1b2382d7f8a4ee509d9245db4450d926a0b24146
- https://github.com/Vanessa219/vditor
- https://securitylab.github.com/advisories/GHSL-2021-1006-vditor
