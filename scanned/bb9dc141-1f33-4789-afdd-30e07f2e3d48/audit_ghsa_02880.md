# [M] Inclusion of Functionality from Untrusted Control Sphere in CKEditor 4

## Summary
Severity: Medium
Advisory: GHSA-wpvm-wqr4-p7cw
CVE: CVE-2021-26272
CWE: CWE-829
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-10-13
Source: https://github.com/advisories/GHSA-wpvm-wqr4-p7cw
Type: github-advisory

## Affected
- npm: `ckeditor4` — affected >=0 <4.16.0

## Details
It was possible to execute a ReDoS-type attack inside CKEditor 4 before 4.16 by persuading a victim to paste crafted URL-like text into the editor, and then press Enter or Space (in the Autolink plugin).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-26272
- https://ckeditor.com/blog/CKEditor-4.16-with-improved-image-pasting-High-Contrast-support-and-a-new-color-API/#security-comes-first
- https://github.com/ckeditor/ckeditor4
- https://github.com/ckeditor/ckeditor4/blob/major/CHANGES.md#ckeditor-416
- https://www.oracle.com//security-alerts/cpujul2021.html
- https://www.oracle.com/security-alerts/cpujan2022.html
- https://www.oracle.com/security-alerts/cpuoct2021.html
