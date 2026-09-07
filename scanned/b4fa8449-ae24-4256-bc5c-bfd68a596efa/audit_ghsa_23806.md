# [C] Magento 2 Community Edition Insecure Component

## Summary
Severity: Critical
Advisory: GHSA-xgcp-59g2-wm8g
CVE: CVE-2019-8136
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-xgcp-59g2-wm8g
Type: github-advisory

## Affected
- Packagist: `magento/community-edition` — affected >=2.2.0 <2.2.10
- Packagist: `magento/community-edition` — affected >=2.3.0 <2.3.2-p1

## Details
An insecure component vulnerability exists in Magento 2.2 prior to 2.2.10, Magento 2.3 prior to 2.3.3 or 2.3.2-p1. Magento 2 codebase leveraged outdated versions of HTTP specification abstraction implemented in symphony component.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-8136
- https://github.com/FriendsOfPHP/security-advisories/blob/master/magento/product-community-edition/CVE-2019-8136.yaml
- https://github.com/magento/magento2
- https://magento.com/security/patches/magento-2.3.3-and-2.2.10-security-update
- https://web.archive.org/web/20220121051105/https://magento.com/security/patches/magento-2.3.3-and-2.2.10-security-update
