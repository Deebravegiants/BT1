# [M] Magento Broken authentication and session managememt

## Summary
Severity: Medium
Advisory: GHSA-92ph-xm9v-cg3j
CVE: CVE-2019-8108
CWE: CWE-287
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-92ph-xm9v-cg3j
Type: github-advisory

## Affected
- Packagist: `magento/community-edition` — affected >=2.2 <2.2.10
- Packagist: `magento/community-edition` — affected >=2.3 <2.3.2-p2

## Details
Insecure authentication and session management vulnerability exists in Magento 2.2 prior to 2.2.10, Magento 2.3 prior to 2.3.3 or 2.3.2-p1. An authenticated user can manipulate session validation setting for a storefront that leads to insecure authentication and session management.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-8108
- https://github.com/FriendsOfPHP/security-advisories/blob/master/magento/product-community-edition/CVE-2019-8108.yaml
- https://github.com/magento/magento2
- https://magento.com/security/patches/magento-2.3.3-and-2.2.10-security-update
