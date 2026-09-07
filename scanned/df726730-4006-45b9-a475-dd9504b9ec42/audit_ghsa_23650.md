# [H] Image Resizer Cross-Site Request Forgery (CSRF)

## Summary
Severity: High
Advisory: GHSA-5v5q-3m7m-97j7
CVE: CVE-2020-13458
CWE: CWE-352
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-5v5q-3m7m-97j7
Type: github-advisory

## Affected
- Packagist: `verbb/image-resizer` — affected >=0 <2.0.9

## Details
An issue was discovered in the Image Resizer plugin before 2.0.9 for Craft CMS. There are CSRF issues with the log-clear controller action.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-13458
- https://github.com/verbb/image-resizer
- https://github.com/verbb/image-resizer/blob/craft-3/CHANGELOG.md
