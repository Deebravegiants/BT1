# [M] Cross-Site Request Forgery in Anchor CMS

## Summary
Severity: Medium
Advisory: GHSA-2whx-ccr7-fxqm
CVE: CVE-2024-29338
CWE: CWE-352
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:L/A:L (CVSS_V3)
Published: 2024-03-22
Source: https://github.com/advisories/GHSA-2whx-ccr7-fxqm
Type: github-advisory

## Affected
- Packagist: `anchorcms/anchor-cms` — affected >=0

## Details
Anchor CMS v0.12.7 was discovered to contain a Cross-Site Request Forgery (CSRF) via `/anchor/admin/categories/delete/2`.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-29338
- https://github.com/PWwwww123/cms/blob/main/1.md
- https://github.com/anchorcms/anchor-cms
