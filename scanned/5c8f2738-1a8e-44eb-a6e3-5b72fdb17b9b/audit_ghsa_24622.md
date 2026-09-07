# [M] Magento 2 Community Edition Incorrect Authorization

## Summary
Severity: Medium
Advisory: GHSA-f2g3-3c6q-4478
CVE: CVE-2020-24401
CWE: CWE-863
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-f2g3-3c6q-4478
Type: github-advisory

## Affected
- Packagist: `magento/community-edition` — affected >=0 <2.4.1
- Packagist: `magento/project-community-edition` — affected >=0

## Details
Magento versions 2.4.0 and 2.3.5p1 (and earlier) are affected by an incorrect authorization vulnerability. A user can still access resources provisioned under their old role after an administrator removes the role or disables the user's account.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-24401
- https://github.com/magento/magento2
- https://helpx.adobe.com/security/products/magento/apsb20-59.html
