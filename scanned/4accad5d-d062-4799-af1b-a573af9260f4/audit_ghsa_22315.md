# [M] Magento 2 Community Edition Injection Vulnerability

## Summary
Severity: Medium
Advisory: GHSA-hxmp-jcqj-83hm
CVE: CVE-2019-7889
CWE: CWE-74
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-hxmp-jcqj-83hm
Type: github-advisory

## Affected
- Packagist: `magento/community-edition` — affected >=2.1.0 <2.1.18
- Packagist: `magento/community-edition` — affected >=2.2.0 <2.2.9
- Packagist: `magento/community-edition` — affected >=2.3.0 <2.3.2

## Details
An injection vulnerability exists in Magento Open Source prior to 1.9.4.2, and Magento Commerce prior to 1.14.4.2, Magento 2.1 prior to 2.1.18, Magento 2.2 prior to 2.2.9, Magento 2.3 prior to 2.3.2. An authenticated user with marketing manipulation privileges can invoke methods that alter data of the underlying model followed by corresponding database modifications.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-7889
- https://github.com/FriendsOfPHP/security-advisories/blob/master/magento/magento1ce/CVE-2019-7889.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/magento/magento1ee/CVE-2019-7889.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/magento/product-community-edition/CVE-2019-7889.yaml
- https://github.com/magento/magento2
- https://magento.com/security/patches/magento-2.3.2-2.2.9-and-2.1.18-security-update-13
