# [M] Image Resizer Cross-site Scripting (XSS) in the Bulk Resize action

## Summary
Severity: Medium
Advisory: GHSA-p7rm-gh9g-5fr8
CVE: CVE-2020-13459
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-p7rm-gh9g-5fr8
Type: github-advisory

## Affected
- Packagist: `verbb/image-resizer` — affected >=0 <2.0.9

## Details
An issue was discovered in the Image Resizer plugin before 2.0.9 for Craft CMS. There is stored XSS in the Bulk Resize action.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-13459
- https://github.com/verbb/image-resizer
- https://github.com/verbb/image-resizer/blob/craft-3/CHANGELOG.md
