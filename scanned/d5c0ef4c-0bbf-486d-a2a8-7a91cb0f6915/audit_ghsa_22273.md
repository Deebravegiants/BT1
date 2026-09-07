# [C] Magento 2 Community Edition SQLi Vulnerability

## Summary
Severity: Critical
Advisory: GHSA-4j6w-9rf8-hg7r
CVE: CVE-2019-7139
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-4j6w-9rf8-hg7r
Type: github-advisory

## Affected
- Packagist: `magento/community-edition` — affected >=2.1.0 <2.1.18
- Packagist: `magento/community-edition` — affected >=2.2.0 <2.2.9
- Packagist: `magento/community-edition` — affected >=2.3.0 <2.3.2

## Details
An unauthenticated user can execute SQL statements that allow arbitrary read access to the underlying database, which causes sensitive data leakage. This issue is fixed in Magento 2.1 prior to 2.1.18, Magento 2.2 prior to 2.2.9, Magento 2.3 prior to 2.3.2.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-7139
- https://github.com/FriendsOfPHP/security-advisories/blob/master/magento/magento1ce/CVE-2019-7139.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/magento/magento1ee/CVE-2019-7139.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/magento/product-community-edition/CVE-2019-7139.yaml
- https://github.com/magento/magento2
- https://magento.com/security/patches/magento-2.3.2-2.2.9-and-2.1.18-security-update-13
- https://magento.com/security/patches/supee-11086
- https://web.archive.org/web/20211206084839/https://magento.com/security/patches/magento-2.3.2-2.2.9-and-2.1.18-security-update-13
- https://www.ambionics.io/blog/magento-sqli
