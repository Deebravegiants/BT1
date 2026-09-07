# [H] Magento 2 Community Edition Unsafe File Upload

## Summary
Severity: High
Advisory: GHSA-v527-6h5r-cfg8
CVE: CVE-2019-7871
CWE: CWE-94
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-v527-6h5r-cfg8
Type: github-advisory

## Affected
- Packagist: `magento/community-edition` — affected >=2.1.0 <2.1.18
- Packagist: `magento/community-edition` — affected >=2.2.0 <2.2.9
- Packagist: `magento/community-edition` — affected >=2.3.0 <2.3.2

## Details
A security bypass exists in Magento 2.1 prior to 2.1.18, Magento 2.2 prior to 2.2.9, Magento 2.3 prior to 2.3.2 that could be abused to execute arbitrary PHP code. An authenticated user can bypass security protections that prevent arbitrary PHP script upload via form data injection.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-7871
- https://github.com/FriendsOfPHP/security-advisories/blob/master/magento/product-community-edition/CVE-2019-7871.yaml
- https://github.com/magento/magento2
- https://magento.com/security/patches/magento-2.3.2-2.2.9-and-2.1.18-security-update-13
- https://web.archive.org/web/20211206084839/https://magento.com/security/patches/magento-2.3.2-2.2.9-and-2.1.18-security-update-13
