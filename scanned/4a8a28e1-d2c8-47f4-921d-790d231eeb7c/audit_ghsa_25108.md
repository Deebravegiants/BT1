# [H] Magento Information Disclosure via File upload functionality

## Summary
Severity: High
Advisory: GHSA-32x5-6p4q-q8jh
CVE: CVE-2019-8093
CWE: CWE-434
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-32x5-6p4q-q8jh
Type: github-advisory

## Affected
- Packagist: `magento/community-edition` — affected >=2.2 <2.2.10
- Packagist: `magento/community-edition` — affected >=2.3 <2.3.2-p1

## Details
An arbitrary file access vulnerability exists in Magento 2.2 prior to 2.2.10, Magento 2.3 prior to 2.3.3 or 2.3.2-p1. An authenticated user can leverage file upload controller for downloadable products to read/delete an arbitary files.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-8093
- https://github.com/FriendsOfPHP/security-advisories/blob/master/magento/product-community-edition/CVE-2019-8093.yaml
- https://github.com/magento/magento2
- https://magento.com/security/patches/magento-2.3.3-and-2.2.10-security-update
