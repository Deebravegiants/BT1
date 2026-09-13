# [M] CKEditor 4 ReDoS Vulnerability

## Summary
Severity: Medium
Advisory: GHSA-jv4c-7jqq-m34x
CVE: CVE-2021-26271
CWE: CWE-1333
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-jv4c-7jqq-m34x
Type: github-advisory

## Affected
- npm: `ckeditor4-dev` — affected >=0 <4.16

## Details
It was possible to execute a ReDoS-type attack inside CKEditor 4 before 4.16 by persuading a victim to paste crafted text into the Styles input of specific dialogs (in the Advanced Tab for Dialogs plugin).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-26271
- https://github.com/ckeditor/ckeditor4
- https://github.com/ckeditor/ckeditor4/blob/major/CHANGES.md#ckeditor-416
- https://web.archive.org/web/20210128132707/https://ckeditor.com/blog/CKEditor-4.16-with-improved-image-pasting-High-Contrast-support-and-a-new-color-API/#security-comes-first
- https://www.oracle.com//security-alerts/cpujul2021.html
- https://www.oracle.com/security-alerts/cpuoct2021.html
