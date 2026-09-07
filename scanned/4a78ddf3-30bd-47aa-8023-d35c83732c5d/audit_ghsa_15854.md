# [M] Magento Open Source Time-of-check Time-of-use (TOCTOU) Race Condition vulnerability

## Summary
Severity: Medium
Advisory: GHSA-47jp-46c9-25vf
CVE: CVE-2024-45120
CWE: CWE-367
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2024-10-10
Source: https://github.com/advisories/GHSA-47jp-46c9-25vf
Type: github-advisory

## Affected
- Packagist: `magento/community-edition` — affected >=2.4.7-beta1 <2.4.7-p3
- Packagist: `magento/community-edition` — affected >=2.4.6-p1 <2.4.6-p8
- Packagist: `magento/community-edition` — affected >=2.4.5-p1 <2.4.5-p10
- Packagist: `magento/community-edition` — affected >=0 <2.4.4-p11
- Packagist: `magento/community-edition` — affected 2.4.7
- Packagist: `magento/community-edition` — affected 2.4.6
- Packagist: `magento/community-edition` — affected 2.4.5
- Packagist: `magento/community-edition` — affected 2.4.4

## Details
Adobe Commerce versions 2.4.7-p2, 2.4.6-p7, 2.4.5-p9, 2.4.4-p10 and earlier are affected by a Time-of-check Time-of-use (TOCTOU) Race Condition vulnerability that could lead to a security feature bypass. An attacker could exploit this vulnerability to alter a condition between the check and the use of a resource, having a low impact on integrity. Exploitation of this issue requires user interaction.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-45120
- https://github.com/magento/magento2
- https://helpx.adobe.com/security/products/magento/apsb24-73.html
