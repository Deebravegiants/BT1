# [M] Magento Improper Access Control leads to Security feature bypass

## Summary
Severity: Medium
Advisory: GHSA-6wq7-cg9h-mj6q
CVE: CVE-2025-27190
CWE: CWE-284
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2025-04-08
Source: https://github.com/advisories/GHSA-6wq7-cg9h-mj6q
Type: github-advisory

## Affected
- Packagist: `magento/project-community-edition` — affected >=0
- Packagist: `magento/community-edition` — affected >=2.4.7-beta1 <2.4.7-p5
- Packagist: `magento/community-edition` — affected >=2.4.6-p1 <2.4.6-p10
- Packagist: `magento/community-edition` — affected >=2.4.5-p1 <2.4.5-p12
- Packagist: `magento/community-edition` — affected >=0 <2.4.4-p13
- Packagist: `magento/community-edition` — affected >=2.4.8-beta1 <2.4.8-beta2
- Packagist: `magento/community-edition` — affected 2.4.5
- Packagist: `magento/community-edition` — affected 2.4.4
- Packagist: `magento/community-edition` — affected 2.4.6
- Packagist: `magento/community-edition` — affected 2.4.7

## Details
Magento versions 2.4.7-p4, 2.4.6-p9, 2.4.5-p11, 2.4.4-p12, 2.4.8-beta2 and earlier are affected by an Improper Access Control vulnerability that could result in a Security feature bypass. An attacker could leverage this vulnerability to bypass security measures and gain unauthorized access. Exploitation of this issue does not require user interaction.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-27190
- https://github.com/magento/magento2
- https://helpx.adobe.com/security/products/magento/apsb25-26.html
