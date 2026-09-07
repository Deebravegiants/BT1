# [M] Magento 2 Community Edition Cross-site Scripting Vulnerability

## Summary
Severity: Medium
Advisory: GHSA-rj8f-g5gm-jw5c
CVE: CVE-2019-7887
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:H/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-rj8f-g5gm-jw5c
Type: github-advisory

## Affected
- Packagist: `magento/community-edition` — affected >=2.1.0 <2.1.18
- Packagist: `magento/community-edition` — affected >=2.2.0 <2.2.9
- Packagist: `magento/community-edition` — affected >=2.3.0 <2.3.2

## Details
A reflected cross-site scripting vulnerability exists in the admin panel of Magento Open Source prior to 1.9.4.2, and Magento Commerce prior to 1.14.4.2, Magento 2.1 prior to 2.1.18, Magento 2.2 prior to 2.2.9, Magento 2.3 prior to 2.3.2 when the feature that adds a secret key to the Admin URL is disabled.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-7887
- https://github.com/FriendsOfPHP/security-advisories/blob/master/magento/magento1ce/CVE-2019-7887.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/magento/magento1ee/CVE-2019-7887.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/magento/product-community-edition/CVE-2019-7887.yaml
- https://magento.com/security/patches/magento-2.3.2-2.2.9-and-2.1.18-security-update-23
- https://web.archive.org/web/20220121051916/https://magento.com/security/patches/magento-2.3.2-2.2.9-and-2.1.18-security-update-23
