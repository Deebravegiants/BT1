# [M] Magento Cross-Site Scripting via store name

## Summary
Severity: Medium
Advisory: GHSA-mhwc-4w67-xq2c
CVE: CVE-2019-8128
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-mhwc-4w67-xq2c
Type: github-advisory

## Affected
- Packagist: `magento/community-edition` — affected >=2.2 <2.2.10
- Packagist: `magento/community-edition` — affected >=2.3 <2.3.2-p1

## Details
A stored cross-site scripting (XSS) vulnerability exists in Magento 2.2 prior to 2.2.10, Magento 2.3 prior to 2.3.3 or 2.3.2-p1. An authenticated user can exploit it by injecting malicious Javascript into the name of main website.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-8128
- https://github.com/FriendsOfPHP/security-advisories/blob/master/magento/product-community-edition/CVE-2019-8128.yaml
- https://github.com/magento/magento2
- https://magento.com/security/patches/magento-2.3.3-and-2.2.10-security-update
