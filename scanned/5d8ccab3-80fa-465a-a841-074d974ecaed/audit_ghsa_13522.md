# [M] Magento Open Source allows SQL Injection 

## Summary
Severity: Medium
Advisory: GHSA-ggr8-3hwx-4f2m
CVE: CVE-2023-38221
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:H/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2023-10-13
Source: https://github.com/advisories/GHSA-ggr8-3hwx-4f2m
Type: github-advisory

## Affected
- Packagist: `magento/community-edition` — affected >=2.4.7-beta1 <2.4.7-beta2
- Packagist: `magento/community-edition` — affected 2.4.6
- Packagist: `magento/community-edition` — affected 2.4.5
- Packagist: `magento/community-edition` — affected 2.4.4
- Packagist: `magento/community-edition` — affected >=2.4.6-p1 <2.4.6-p3
- Packagist: `magento/community-edition` — affected >=2.4.5-p1 <2.4.5-p5
- Packagist: `magento/community-edition` — affected >=2.4.4-p1 <2.4.4-p6
- Packagist: `magento/project-community-edition` — affected >=0

## Details
Adobe Commerce versions 2.4.7-beta1 (and earlier), 2.4.6-p2 (and earlier), 2.4.5-p4 (and earlier) and 2.4.4-p5 (and earlier) are affected by an Improper Neutralization of Special Elements used in an SQL Command ('SQL Injection') vulnerability that could lead in arbitrary code execution by an admin-privilege authenticated attacker. Exploitation of this issue does not require user interaction and attack complexity is high as it requires knowledge of tooling beyond just using the UI.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-38221
- https://github.com/magento/magento2
- https://helpx.adobe.com/security/products/magento/apsb23-50.html
