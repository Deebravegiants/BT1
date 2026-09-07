# [M] EpicEditor XSS Vulnerability

## Summary
Severity: Medium
Advisory: GHSA-4wc5-gfgh-4vjx
CVE: CVE-2017-6589
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-4wc5-gfgh-4vjx
Type: github-advisory

## Affected
- npm: `epiceditor` — affected >=0

## Details
EpicEditor through 0.2.3 has Cross-Site Scripting because of an insecure default marked.js configuration. An example attack vector is a crafted IMG element in an HTML document.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-6589
- https://bad.code.blog/2017/03/09/epiceditor-cross-site-scripting
- https://github.com/OscarGodson/EpicEditor
