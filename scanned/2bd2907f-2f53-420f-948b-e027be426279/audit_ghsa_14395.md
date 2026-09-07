# [M] Magento Open Source allows Improper Access Control

## Summary
Severity: Medium
Advisory: GHSA-4h7p-4vq8-g2gh
CVE: CVE-2023-22250
CWE: CWE-284
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2023-03-27
Source: https://github.com/advisories/GHSA-4h7p-4vq8-g2gh
Type: github-advisory

## Affected
- Packagist: `magento/community-edition` — affected >=2.4.4-p1 <2.4.4-p3
- Packagist: `magento/community-edition` — affected 2.4.4
- Packagist: `magento/community-edition` — affected 2.4.5
- Packagist: `magento/community-edition` — affected >=2.4.5-p1 <2.4.5-p2
- Packagist: `magento/project-community-edition` — affected >=0

## Details
Adobe Commerce versions 2.4.4-p2 (and earlier) and 2.4.5-p1 (and earlier) are affected by an Improper Access Control vulnerability that could result in a Security feature bypass. An attacker could leverage this vulnerability to impact the availability of a user's minor feature. Exploitation of this issue does not require user interaction.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-22250
- https://github.com/magento/magento2
- https://helpx.adobe.com/security/products/magento/apsb23-17.html
