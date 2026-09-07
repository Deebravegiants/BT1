# [M] Magento Stored cross-site scripting in admin panel

## Summary
Severity: Medium
Advisory: GHSA-p8gw-x2p7-vc73
CVE: CVE-2019-7863
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:H/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-p8gw-x2p7-vc73
Type: github-advisory

## Affected
- Packagist: `magento/community-edition` — affected >=2.1 <2.1.18
- Packagist: `magento/community-edition` — affected >=2.2 <2.2.9
- Packagist: `magento/community-edition` — affected >=2.3 <2.3.2

## Details
A stored cross-site scripting vulnerability exists in the admin panel for Magento 2.1 prior to 2.1.18, Magento 2.2 prior to 2.2.9, Magento 2.3 prior to 2.3.2. This can be exploited by an authenticated user with access to products and categories.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-7863
- https://github.com/FriendsOfPHP/security-advisories/blob/master/magento/product-community-edition/CVE-2019-7863.yaml
- https://github.com/magento/magento2
- https://web.archive.org/web/20201001022642/https://magento.com/security/patches/magento-2.3.2-2.2.9-and-2.1.18-security-update-23
