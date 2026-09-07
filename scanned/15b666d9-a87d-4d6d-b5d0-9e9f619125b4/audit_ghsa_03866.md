# [M] Magento Cross-Site Scripting via Attribute Set Name

## Summary
Severity: Medium
Advisory: GHSA-xv69-f7x5-r4qw
CVE: CVE-2019-8145
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2019-11-12
Source: https://github.com/advisories/GHSA-xv69-f7x5-r4qw
Type: github-advisory

## Affected
- Packagist: `magento/community-edition` — affected >=2.2 <2.2.10
- Packagist: `magento/community-edition` — affected >=2.3 <2.3.2-p1

## Details
A stored cross-site scripting (XSS) vulnerability exists in Magento 2.2 prior to 2.2.10, Magento 2.3 prior to 2.3.3 or 2.3.2-p1. An authenticated user can inject arbitrary JavaScript code into the attribute set name when listing the products.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-8145
- https://github.com/FriendsOfPHP/security-advisories/blob/master/magento/product-community-edition/CVE-2019-8145.yaml
- https://github.com/magento/magento2
- https://magento.com/security/patches/magento-2.3.3-and-2.2.10-security-update
