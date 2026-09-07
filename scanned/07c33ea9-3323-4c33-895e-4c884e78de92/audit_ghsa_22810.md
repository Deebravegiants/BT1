# [M] Magento 2 Community Weak PRNG

## Summary
Severity: Medium
Advisory: GHSA-c4r2-3f9r-rwp8
CVE: CVE-2019-8113
CWE: CWE-338
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-c4r2-3f9r-rwp8
Type: github-advisory

## Affected
- Packagist: `magento/community-edition` — affected >=2.2.0 <2.2.10
- Packagist: `magento/community-edition` — affected >=2.3.0 <2.3.2-p1

## Details
Magento 2.2 prior to 2.2.10, Magento 2.3 prior to 2.3.3 or 2.3.2-p1 uses cryptographically weak random number generator to brute-force the confirmation code for customer registration.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-8113
- https://github.com/FriendsOfPHP/security-advisories/blob/master/magento/product-community-edition/CVE-2019-8113.yaml
- https://github.com/magento/magento2
- https://magento.com/security/patches/magento-2.3.3-and-2.2.10-security-update
- https://web.archive.org/web/20220121051105/https://magento.com/security/patches/magento-2.3.3-and-2.2.10-security-update
