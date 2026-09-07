# [H] Magento 2 Community Edition Path Traversal Vulnerability

## Summary
Severity: High
Advisory: GHSA-hqhf-8jgc-h5hx
CVE: CVE-2019-7859
CWE: CWE-22
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-hqhf-8jgc-h5hx
Type: github-advisory

## Affected
- Packagist: `magento/community-edition` — affected >=2.1.0 <2.1.18
- Packagist: `magento/community-edition` — affected >=2.2.0 <2.2.9
- Packagist: `magento/community-edition` — affected >=2.3.0 <2.3.2

## Details
A path traversal vulnerability in the WYSIWYG editor for Magento 2.1 prior to 2.1.18, Magento 2.2 prior to 2.2.9, Magento 2.3 prior to 2.3.2 could result in unauthorized access to uploaded images due to insufficient access control.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-7859
- https://github.com/FriendsOfPHP/security-advisories/blob/master/magento/product-community-edition/CVE-2019-7859.yaml
- https://github.com/magento/magento2
- https://magento.com/security/patches/magento-2.3.2-2.2.9-and-2.1.18-security-update-23
- https://web.archive.org/web/20220127030535/https://magento.com/security/patches/magento-2.3.2-2.2.9-and-2.1.18-security-update-24
