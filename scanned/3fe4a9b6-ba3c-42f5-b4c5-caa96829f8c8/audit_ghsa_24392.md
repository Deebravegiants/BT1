# [M] Magento Injection vulnerability via email templates

## Summary
Severity: Medium
Advisory: GHSA-94q8-gx29-6mqv
CVE: CVE-2019-8143
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-94q8-gx29-6mqv
Type: github-advisory

## Affected
- Packagist: `magento/community-edition` — affected >=2.2 <2.2.10
- Packagist: `magento/community-edition` — affected >=2.3 <2.3.2-p1

## Details
A SQL injection vulnerability exists in Magento 2.2 prior to 2.2.10, Magento 2.3 prior to 2.3.3 or 2.3.2-p1. An authenticated user with access to email templates can send malicious SQL queries and obtain access to sensitive information stored in the database.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-8143
- https://github.com/FriendsOfPHP/security-advisories/blob/master/magento/product-community-edition/CVE-2019-8143.yaml
- https://github.com/magento/magento2
- https://magento.com/security/patches/magento-2.3.3-and-2.2.10-security-update
