# [H] Cross Site Request Forgery in kindeditor

## Summary
Severity: High
Advisory: GHSA-3ww4-cp53-6g2x
CVE: CVE-2021-42228
CWE: CWE-352
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-10-18
Source: https://github.com/advisories/GHSA-3ww4-cp53-6g2x
Type: github-advisory

## Affected
- npm: `kindeditor` — affected >=0

## Details
Cross Site Request Forgery (CSRF) vulnerability exists in KindEditor 4.1.x. First, you upload an html file containing csrf on the website that uses a google editor, (you only need to search in google: inurl:/examples/uploadbutton.html) and then use the authority of this website to trick users into clicking your malicious html link.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-42228
- https://github.com/kindsoft/kindeditor/issues/337
- https://github.com/kindsoft/kindeditor
