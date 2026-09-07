# [M] Magento Open Source allows Improper Authorization

## Summary
Severity: Medium
Advisory: GHSA-grc6-r6f8-xj7c
CVE: CVE-2023-38220
CWE: CWE-285
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-10-13
Source: https://github.com/advisories/GHSA-grc6-r6f8-xj7c
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
Adobe Commerce versions 2.4.7-beta1 (and earlier), 2.4.6-p2 (and earlier), 2.4.5-p4 (and earlier) and 2.4.4-p5 (and earlier) are affected by an Improper Authorization vulnerability that could lead in a security feature bypass in a way that an attacker could access unauthorised data. Exploitation of this issue does not require user interaction.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-38220
- https://github.com/magento/magento2
- https://helpx.adobe.com/security/products/magento/apsb23-50.html
