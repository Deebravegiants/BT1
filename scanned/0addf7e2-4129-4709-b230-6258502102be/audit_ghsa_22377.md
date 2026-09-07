# [H] Magento 2 Community Edition IDOR Vulnerability

## Summary
Severity: High
Advisory: GHSA-3pgc-7jf3-5x5g
CVE: CVE-2019-7890
CWE: CWE-639
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-3pgc-7jf3-5x5g
Type: github-advisory

## Affected
- Packagist: `magento/community-edition` — affected >=2.1 <2.1.18
- Packagist: `magento/community-edition` — affected >=2.2 <2.2.9
- Packagist: `magento/community-edition` — affected >=2.3 <2.3.2

## Details
An Insecure Direct Object Reference (IDOR) vulnerability exists in the order processing workflow of Magento 2.1 prior to 2.1.18, Magento 2.2 prior to 2.2.9, Magento 2.3 prior to 2.3.2. This can lead to unauthorized access to order details.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-7890
- https://github.com/FriendsOfPHP/security-advisories/blob/master/magento/product-community-edition/CVE-2019-7890.yaml
- https://magento.com/security/patches/magento-2.3.2-2.2.9-and-2.1.18-security-update-23
- https://web.archive.org/web/20220121051916/https://magento.com/security/patches/magento-2.3.2-2.2.9-and-2.1.18-security-update-23
