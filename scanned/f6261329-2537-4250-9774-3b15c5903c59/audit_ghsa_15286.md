# [M] Magento Improper Access Control Leads to Privilege escalation

## Summary
Severity: Medium
Advisory: GHSA-x6f9-hv9r-fgq4
CVE: CVE-2024-39414
CWE: CWE-284
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2024-08-14
Source: https://github.com/advisories/GHSA-x6f9-hv9r-fgq4
Type: github-advisory

## Affected
- Packagist: `magento/project-community-edition` — affected >=0
- Packagist: `magento/community-edition` — affected >=2.4.7-beta1 <2.4.7-p2
- Packagist: `magento/community-edition` — affected >=2.4.6-p1 <2.4.6-p7
- Packagist: `magento/community-edition` — affected >=2.4.5-p1 <2.4.5-p9
- Packagist: `magento/community-edition` — affected >=0 <2.4.4-p10
- Packagist: `magento/community-edition` — affected 2.4.4
- Packagist: `magento/community-edition` — affected 2.4.5
- Packagist: `magento/community-edition` — affected 2.4.6
- Packagist: `magento/community-edition` — affected 2.4.7

## Details
Magento versions 2.4.7-p1, 2.4.6-p6, 2.4.5-p8, 2.4.4-p9 and earlier are affected by an Improper Authorization vulnerability that could result in a Security feature bypass. A low-privileged attacker could leverage this vulnerability to bypass security measures and disclose minor information. Exploitation of this issue does not require user interaction.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-39414
- https://github.com/magento/magento2
- https://helpx.adobe.com/security/products/magento/apsb24-61.html
