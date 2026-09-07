# [M] Magento 2 Community Edition CSRF vulnerability

## Summary
Severity: Medium
Advisory: GHSA-w392-68rg-pgg4
CVE: CVE-2019-7947
CWE: CWE-352
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-w392-68rg-pgg4
Type: github-advisory

## Affected
- Packagist: `magento/community-edition` — affected >=2.1.0 <2.1.18
- Packagist: `magento/community-edition` — affected >=2.2.0 <2.2.9
- Packagist: `magento/community-edition` — affected >=2.3.0 <2.3.2

## Details
A cross-site request forgery vulnerability exists in the GiftCardAccount removal feature for Magento Open Source prior to 1.9.4.2, and Magento Commerce prior to 1.14.4.2, Magento 2.1 prior to 2.1.18, Magento 2.2 prior to 2.2.9, Magento 2.3 prior to 2.3.2.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-7947
- https://github.com/FriendsOfPHP/security-advisories/blob/master/magento/magento1ce/CVE-2019-7947.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/magento/magento1ee/CVE-2019-7947.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/magento/product-community-edition/CVE-2019-7947.yaml
- https://magento.com/security/patches/magento-2.3.2-2.2.9-and-2.1.18-security-update-33
- https://web.archive.org/web/20220121011306/https://magento.com/security/patches/magento-2.3.2-2.2.9-and-2.1.18-security-update-33
