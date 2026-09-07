# [M] Magento Open Source allows Uncontrolled Resource Consumption

## Summary
Severity: Medium
Advisory: GHSA-7pfc-834q-h497
CVE: CVE-2023-38251
CWE: CWE-400
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2023-10-13
Source: https://github.com/advisories/GHSA-7pfc-834q-h497
Type: github-advisory

## Affected
- Packagist: `magento/community-edition` — affected >=2.4.7-beta1 <2.4.7-beta2
- Packagist: `magento/community-edition` — affected 2.4.7
- Packagist: `magento/community-edition` — affected 2.4.6
- Packagist: `magento/community-edition` — affected 2.4.5
- Packagist: `magento/community-edition` — affected 2.4.4
- Packagist: `magento/community-edition` — affected >=2.4.6-p1 <2.4.6-p3
- Packagist: `magento/community-edition` — affected >=2.4.5-p1 <2.4.5-p5
- Packagist: `magento/community-edition` — affected >=2.4.4-p1 <2.4.4-p6
- Packagist: `magento/project-community-edition` — affected >=0

## Details
Adobe Commerce versions 2.4.7-beta1 (and earlier), 2.4.6-p2 (and earlier), 2.4.5-p4 (and earlier) and 2.4.4-p5 (and earlier) are affected by an Uncontrolled Resource Consumption vulnerability that could lead into a minor application denial-of-service. Exploitation of this issue does not require user interaction.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-38251
- https://github.com/magento/magento2
- https://helpx.adobe.com/security/products/magento/apsb23-50.html
