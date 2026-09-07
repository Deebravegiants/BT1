# [H] Magento OS Command ('OS Command Injection') vulnerability

## Summary
Severity: High
Advisory: GHSA-2ff6-837j-hg5x
CVE: CVE-2024-39402
CWE: CWE-78
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2024-08-14
Source: https://github.com/advisories/GHSA-2ff6-837j-hg5x
Type: github-advisory

## Affected
- Packagist: `magento/project-community-edition` — affected >=0
- Packagist: `magento/community-edition` — affected >=2.4.7-beta1 <2.4.7-p2
- Packagist: `magento/community-edition` — affected >=2.4.6-p1 <2.4.6-p7
- Packagist: `magento/community-edition` — affected >=2.4.5-p1 <2.4.5-p9
- Packagist: `magento/community-edition` — affected >=2.4.4-p1 <2.4.4-p10
- Packagist: `magento/community-edition` — affected 2.4.7
- Packagist: `magento/community-edition` — affected 2.4.6
- Packagist: `magento/community-edition` — affected 2.4.5
- Packagist: `magento/community-edition` — affected 2.4.4

## Details
Magento versions 2.4.7-p1, 2.4.6-p6, 2.4.5-p8, 2.4.4-p9 and earlier are affected by an Improper Neutralization of Special Elements used in an OS Command ('OS Command Injection') vulnerability that could lead in arbitrary code execution by an admin attacker. Exploitation of this issue requires user interaction and scope is changed.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-39402
- https://github.com/magento/magento2
- https://helpx.adobe.com/security/products/magento/apsb24-61.html
