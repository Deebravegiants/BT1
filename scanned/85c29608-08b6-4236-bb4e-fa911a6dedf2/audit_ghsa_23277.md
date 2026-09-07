# [M] Magento 2 Community Edition Arbitrary File Deletion

## Summary
Severity: Medium
Advisory: GHSA-2cg3-w597-rjfv
CVE: CVE-2019-8107
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-2cg3-w597-rjfv
Type: github-advisory

## Affected
- Packagist: `magento/community-edition` — affected >=2.2.0 <2.2.10
- Packagist: `magento/community-edition` — affected >=2.3.0 <2.3.2-p1

## Details
An arbitrary file deletion vulnerability exists in Magento 2.2 prior to 2.2.10, Magento 2.3 prior to 2.3.3 or 2.3.2-p1. An authenticated user with export data transfer privileges can craft a request to perform arbitrary file deletion.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-8107
- https://github.com/FriendsOfPHP/security-advisories/blob/master/magento/product-community-edition/CVE-2019-8107.yaml
- https://github.com/magento/magento2
- https://magento.com/security/patches/magento-2.3.3-and-2.2.10-security-update
- https://web.archive.org/web/20220121051105/https://magento.com/security/patches/magento-2.3.3-and-2.2.10-security-update
