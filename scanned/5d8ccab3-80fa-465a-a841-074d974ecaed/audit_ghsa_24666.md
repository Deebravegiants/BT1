# [M] Magento 2 Community Edition Insufficient Access Controls

## Summary
Severity: Medium
Advisory: GHSA-5hcx-vg88-hgpm
CVE: CVE-2019-7904
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-5hcx-vg88-hgpm
Type: github-advisory

## Affected
- Packagist: `magento/community-edition` — affected >=2.1.0 <2.1.18
- Packagist: `magento/community-edition` — affected >=2.2.0 <2.2.9
- Packagist: `magento/community-edition` — affected >=2.3.0 <2.3.2

## Details
Insufficient enforcement of user access controls in Magento 2.1 prior to 2.1.18, Magento 2.2 prior to 2.2.9, Magento 2.3 prior to 2.3.2 could enable a low-privileged user to make unauthorized environment configuration changes.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-7904
- https://github.com/FriendsOfPHP/security-advisories/blob/master/magento/product-community-edition/CVE-2019-7904.yaml
- https://magento.com/security/patches/magento-2.3.2-2.2.9-and-2.1.18-security-update-13
- https://web.archive.org/web/20211206084839/https://magento.com/security/patches/magento-2.3.2-2.2.9-and-2.1.18-security-update-13
