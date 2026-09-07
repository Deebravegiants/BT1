# [M] Magento Business Logic Error vulnerability

## Summary
Severity: Medium
Advisory: GHSA-6ff8-jrfg-43hh
CVE: CVE-2025-24425
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2025-02-11
Source: https://github.com/advisories/GHSA-6ff8-jrfg-43hh
Type: github-advisory

## Affected
- Packagist: `magento/community-edition` — affected >=2.4.7-beta1 <2.4.7-p4
- Packagist: `magento/community-edition` — affected >=2.4.6-p1 <2.4.6-p9
- Packagist: `magento/community-edition` — affected >=2.4.5-p1 <2.4.5-p11
- Packagist: `magento/community-edition` — affected >=0 <2.4.4-p12
- Packagist: `magento/community-edition` — affected 2.4.7
- Packagist: `magento/community-edition` — affected 2.4.6
- Packagist: `magento/community-edition` — affected 2.4.5
- Packagist: `magento/community-edition` — affected 2.4.4
- Packagist: `magento/community-edition` — affected 2.4.8-beta1
- Packagist: `magento/project-community-edition` — affected >=0

## Details
Adobe Commerce versions 2.4.7-beta1, 2.4.7-p3, 2.4.6-p8, 2.4.5-p10, 2.4.4-p11 and earlier are affected by a Business Logic Error vulnerability that could result in a security feature bypass. An attacker could exploit this vulnerability to circumvent intended security mechanisms by manipulating the logic of the application's operations causing limited data modification. Exploitation of this issue does not require user interaction.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-24425
- https://github.com/magento/magento2
- https://helpx.adobe.com/security/products/magento/apsb25-08.html
