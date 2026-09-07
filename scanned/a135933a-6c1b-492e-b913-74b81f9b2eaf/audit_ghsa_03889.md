# [H] Using JS libraries with known security vulnerabilities

## Summary
Severity: High
Advisory: GHSA-89ch-hqf9-rgp3
CVE: CVE-2019-8121
Ecosystem: Packagist
Published: 2019-11-12
Source: https://github.com/advisories/GHSA-89ch-hqf9-rgp3
Type: github-advisory

## Affected
- Packagist: `magento/community-edition` — affected >=2.2 <2.2.10
- Packagist: `magento/community-edition` — affected >=2.3 <2.3.3
- Packagist: `magento/product-community-edition` — affected >=2.2 <2.2.10
- Packagist: `magento/product-community-edition` — affected >=2.3 <2.3.2-p2

## Details
An insecure component vulnerability exists in Magento 2.1 prior to 2.1.19, Magento 2.2 prior to 2.2.10, Magento 2.3 prior to 2.3.3. Magento 2 codebase leveraged outdated versions of JS libraries (Bootstrap, jquery, Knockout) with known security vulnerabilities.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-8121
- https://github.com/FriendsOfPHP/security-advisories/blob/master/magento/product-community-edition/CVE-2019-8121.yaml
- https://magento.com/security/patches/magento-2.3.3-and-2.2.10-security-update
