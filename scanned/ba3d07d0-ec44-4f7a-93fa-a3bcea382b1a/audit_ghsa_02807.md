# [M] Cross site scripting in kindeditor

## Summary
Severity: Medium
Advisory: GHSA-wv83-jrfh-rp33
CVE: CVE-2021-42227
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2021-10-18
Source: https://github.com/advisories/GHSA-wv83-jrfh-rp33
Type: github-advisory

## Affected
- npm: `kindeditor` — affected >=0

## Details
Cross SIte Scripting (XSS) vulnerability exists in KindEditor 4.1.x via a Google search inurl:/examples/uploadbutton.html and then the .html file on the website that uses this editor (the file suffix is allowed).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-42227
- https://github.com/kindsoft/kindeditor/issues/336
- https://github.com/kindsoft/kindeditor
