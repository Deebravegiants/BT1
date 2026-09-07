# [M] Magento 2 Community Edition Information Disclosure

## Summary
Severity: Medium
Advisory: GHSA-274w-2j5w-m2xj
CVE: CVE-2019-7899
CWE: CWE-20
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-274w-2j5w-m2xj
Type: github-advisory

## Affected
- Packagist: `magento/community-edition` — affected >=2.1.0 <2.1.18
- Packagist: `magento/community-edition` — affected >=2.2.0 <2.2.9
- Packagist: `magento/community-edition` — affected >=2.3.0 <2.3.2

## Details
Names of disabled downloadable products could be disclosed due to inadequate validation of user input in Magento Open Source prior to 1.9.4.2, and Magento Commerce prior to 1.14.4.2, Magento 2.1 prior to 2.1.18, Magento 2.2 prior to 2.2.9, Magento 2.3 prior to 2.3.2.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-7899
- https://github.com/FriendsOfPHP/security-advisories/blob/master/magento/magento1ce/CVE-2019-7899.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/magento/magento1ee/CVE-2019-7899.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/magento/product-community-edition/CVE-2019-7899.yaml
- https://github.com/magento/magento2
- https://magento.com/security/patches/magento-2.3.2-2.2.9-and-2.1.18-security-update-33
- https://web.archive.org/web/20220121011306/https://magento.com/security/patches/magento-2.3.2-2.2.9-and-2.1.18-security-update-33
