# [M] Magento 2 Community Cryptographic Flaw

## Summary
Severity: Medium
Advisory: GHSA-2w26-gmqm-mc5p
CVE: CVE-2019-7855
CWE: CWE-338
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-2w26-gmqm-mc5p
Type: github-advisory

## Affected
- Packagist: `magento/community-edition` — affected >=2.1.0 <2.1.18
- Packagist: `magento/community-edition` — affected >=2.2.0 <2.2.9
- Packagist: `magento/community-edition` — affected >=2.3.0 <2.3.2

## Details
A cryptograhic flaw in Magento 2.1 prior to 2.1.18, Magento 2.2 prior to 2.2.9, Magento 2.3 prior to 2.3.2 could be abused by an unauthenticated user to discover an invariant used in gift card generation.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-7855
- https://github.com/FriendsOfPHP/security-advisories/blob/master/magento/product-community-edition/CVE-2019-7855.yaml
- https://github.com/magento/magento2
- https://magento.com/security/patches/magento-2.3.2-2.2.9-and-2.1.18-security-update-23
- https://web.archive.org/web/20220121051916/https://magento.com/security/patches/magento-2.3.2-2.2.9-and-2.1.18-security-update-23
