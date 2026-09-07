# [M] Magento Unrestricted file upload vulnerability

## Summary
Severity: Medium
Advisory: GHSA-7pr3-34rg-g53m
CVE: CVE-2019-8140
CWE: CWE-434
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-7pr3-34rg-g53m
Type: github-advisory

## Affected
- Packagist: `magento/community-edition` — affected >=2.2.0 <2.2.10
- Packagist: `magento/community-edition` — affected >=2.3.0 <2.3.3

## Details
An unrestricted file upload vulnerability exists in Magento 2.2 prior to 2.2.10, Magento 2.3 prior to 2.3.3 or 2.3.2-p1. An authenticated admin user can manipulate the Synchronization feature in the Media File Storage of the database to transform uploaded JPEG file into a PHP file.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-8140
- https://github.com/FriendsOfPHP/security-advisories/blob/master/magento/product-community-edition/CVE-2019-8140.yaml
- https://github.com/magento/magento2
- https://magento.com/security/patches/magento-2.3.3-and-2.2.10-security-update
