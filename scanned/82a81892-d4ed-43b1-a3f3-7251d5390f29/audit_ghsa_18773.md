# [H] Magento provides incorrect authorization through a security feature bypass

## Summary
Severity: High
Advisory: GHSA-69x9-xp2j-w8g8
CVE: CVE-2025-54263
CWE: CWE-863
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2025-10-14
Source: https://github.com/advisories/GHSA-69x9-xp2j-w8g8
Type: github-advisory

## Affected
- Packagist: `magento/community-edition` — affected >=2.4.9-alpha1 <2.4.9-alpha3
- Packagist: `magento/community-edition` — affected >=2.4.8-beta1 <2.4.8-p3
- Packagist: `magento/community-edition` — affected >=2.4.7-beta1 <2.4.7-p8
- Packagist: `magento/community-edition` — affected >=0 <2.4.6-p13
- Packagist: `magento/community-edition` — affected 2.4.8
- Packagist: `magento/community-edition` — affected 2.4.7
- Packagist: `magento/community-edition` — affected 2.4.6
- Packagist: `magento/project-community-edition` — affected >=0

## Details
Magento versions 2.4.9-alpha2, 2.4.8-p2, 2.4.7-p7, 2.4.6-p12, 2.4.5-p14, 2.4.4-p15 and earlier are affected by an Incorrect Authorization vulnerability. A low-privileged attacker could leverage this vulnerability to bypass security measures and maintain unauthorized access. Exploitation of this issue does not require user interaction.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-54263
- https://github.com/magento/magento2
- https://helpx.adobe.com/security/products/magento/apsb25-94.html
