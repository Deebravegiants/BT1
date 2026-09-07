# [C] Magento is affected by an improper input validation vulnerability while saving a customer's details

## Summary
Severity: Critical
Advisory: GHSA-gvfx-9m9v-h839
CVE: CVE-2021-36025
CWE: CWE-20
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-gvfx-9m9v-h839
Type: github-advisory

## Affected
- Packagist: `magento/project-community-edition` — affected >=0
- Packagist: `magento/community-edition` — affected >=0 <2.3.7-p1
- Packagist: `magento/community-edition` — affected 2.3.7
- Packagist: `magento/community-edition` — affected >=2.4.2-p1 <2.4.2-p2
- Packagist: `magento/community-edition` — affected 2.4.2

## Details
Magento Commerce versions 2.4.2 (and earlier), 2.4.2-p1 (and earlier) and 2.3.7 (and earlier) are affected by an improper input validation vulnerability while saving a customer's details with a specially crafted file. An authenticated attacker with admin privileges can leverage this vulnerability to achieve remote code execution.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-36025
- https://github.com/magento/magento2
- https://helpx.adobe.com/security/products/magento/apsb21-64.html
