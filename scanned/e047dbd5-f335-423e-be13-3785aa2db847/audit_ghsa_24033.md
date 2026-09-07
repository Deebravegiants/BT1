# [M] MantisBT XSS when uploading an attachment

## Summary
Severity: Medium
Advisory: GHSA-p495-jrpq-p66g
CVE: CVE-2019-15539
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-p495-jrpq-p66g
Type: github-advisory

## Affected
- Packagist: `mantisbt/mantisbt` — affected >=0 <2.21.3

## Details
The proj_doc_edit_page.php Project Documentation feature in MantisBT before 2.21.3 has a stored cross-site scripting (XSS) vulnerability, allowing execution of arbitrary code (if CSP settings permit it) after uploading an attachment with a crafted filename. The code is executed when editing the document's page.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-15539
- https://github.com/mantisbt/mantisbt/commit/bd094dede74ff6e313e286e949e2387233a96eea
- https://github.com/mantisbt/mantisbt
- https://mantisbt.org/bugs/view.php?id=26078
