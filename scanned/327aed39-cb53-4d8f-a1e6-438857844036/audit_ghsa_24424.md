# [M] Magento 2 Community Edition Weak Cryptography

## Summary
Severity: Medium
Advisory: GHSA-hmch-9947-82rj
CVE: CVE-2019-8118
CWE: CWE-312
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-hmch-9947-82rj
Type: github-advisory

## Affected
- Packagist: `magento/community-edition` — affected >=2.1.0 <2.1.19
- Packagist: `magento/community-edition` — affected >=2.2.0 <2.2.10
- Packagist: `magento/community-edition` — affected >=2.3.0 <2.3.3

## Details
Magento 2.1 prior to 2.1.19, Magento 2.2 prior to 2.2.10, Magento 2.3 prior to 2.3.3 uses weak cryptographic function to store the failed login attempts for customer accounts.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-8118
- https://github.com/FriendsOfPHP/security-advisories/blob/master/magento/product-community-edition/CVE-2019-8118.yaml
- https://github.com/magento/magento2
- https://magento.com/security/patches/magento-2.3.3-and-2.2.10-security-update
- https://web.archive.org/web/20220121051105/https://magento.com/security/patches/magento-2.3.3-and-2.2.10-security-update
