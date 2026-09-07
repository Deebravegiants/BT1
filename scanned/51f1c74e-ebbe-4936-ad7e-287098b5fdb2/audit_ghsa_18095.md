# [H] Magento vulnerable to denial of service

## Summary
Severity: High
Advisory: GHSA-xgfm-992v-h2hr
CVE: CVE-2025-49554
CWE: CWE-20
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2025-08-12
Source: https://github.com/advisories/GHSA-xgfm-992v-h2hr
Type: github-advisory

## Affected
- Packagist: `magento/project-community-edition` — affected >=0
- Packagist: `magento/community-edition` — affected >=2.4.9-alpha1 <2.4.9-alpha2
- Packagist: `magento/community-edition` — affected >=2.4.8-beta1 <2.4.8-p2
- Packagist: `magento/community-edition` — affected >=2.4.7-beta1 <2.4.7-p7
- Packagist: `magento/community-edition` — affected >=2.4.6-p1 <2.4.6-p12
- Packagist: `magento/community-edition` — affected >=0 <2.4.5-p14
- Packagist: `magento/community-edition` — affected 2.4.5
- Packagist: `magento/community-edition` — affected 2.4.6
- Packagist: `magento/community-edition` — affected 2.4.7
- Packagist: `magento/community-edition` — affected 2.4.8

## Details
Magento versions 2.4.9-alpha1, 2.4.8-p1, 2.4.7-p6, 2.4.6-p11, 2.4.5-p13, 2.4.4-p14 and earlier are affected by an Improper Input Validation vulnerability that could lead to application denial-of-service. An attacker could exploit this vulnerability by providing specially crafted input, causing the application to crash or become unresponsive. Exploitation of this issue does not require user interaction.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-49554
- https://github.com/magento/magento2
- https://helpx.adobe.com/security/products/magento/apsb25-71.html
