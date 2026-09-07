# [H] Magento 2 Community Edition Security Bypass

## Summary
Severity: High
Advisory: GHSA-p9vf-4jx2-5hpp
CVE: CVE-2019-8112
CWE: CWE-345
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-p9vf-4jx2-5hpp
Type: github-advisory

## Affected
- Packagist: `magento/community-edition` — affected >=2.2.0 <2.2.10
- Packagist: `magento/community-edition` — affected >=2.3.0 <2.3.2-p1

## Details
A security bypass vulnerability exists in Magento 2.2 prior to 2.2.10, Magento 2.3 prior to 2.3.3 or 2.3.2-p1. An unauthenticated user can bypass the email confirmation mechanism via GET request that captures relevant account data obtained from the POST response related to new user creation.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-8112
- https://github.com/FriendsOfPHP/security-advisories/blob/master/magento/product-community-edition/CVE-2019-8112.yaml
- https://github.com/magento/magento2
- https://magento.com/security/patches/magento-2.3.3-and-2.2.10-security-update
- https://web.archive.org/web/20220121051105/https://magento.com/security/patches/magento-2.3.3-and-2.2.10-security-update
