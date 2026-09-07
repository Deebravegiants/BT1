# [H] Magento Open Source allows OS Command Injection

## Summary
Severity: High
Advisory: GHSA-525f-pvj5-vqmq
CVE: CVE-2024-20720
CWE: CWE-78
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2024-02-15
Source: https://github.com/advisories/GHSA-525f-pvj5-vqmq
Type: github-advisory

## Affected
- Packagist: `magento/community-edition` — affected 2.4.6
- Packagist: `magento/community-edition` — affected 2.4.5
- Packagist: `magento/community-edition` — affected 2.4.4
- Packagist: `magento/community-edition` — affected >=2.4.6-p1 <2.4.6-p4
- Packagist: `magento/community-edition` — affected >=2.4.5-p1 <2.4.5-p6
- Packagist: `magento/community-edition` — affected >=2.4.4-p1 <2.4.4-p7
- Packagist: `magento/project-community-edition` — affected >=0

## Details
Adobe Commerce versions 2.4.6-p3, 2.4.5-p5, 2.4.4-p6 and earlier are affected by an Improper Neutralization of Special Elements used in an OS Command ('OS Command Injection') vulnerability that could lead in arbitrary code execution by an attacker. Exploitation of this issue does not require user interaction.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-20720
- https://github.com/magento/magento2
- https://helpx.adobe.com/security/products/magento/apsb24-03.html
