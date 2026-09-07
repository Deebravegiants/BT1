# [H] Magento SQL injection via marketing account with access to email templates variables

## Summary
Severity: High
Advisory: GHSA-45gj-78hc-4mvc
CVE: CVE-2019-8134
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-45gj-78hc-4mvc
Type: github-advisory

## Affected
- Packagist: `magento/community-edition` — affected >=2.2 <2.2.10
- Packagist: `magento/community-edition` — affected >=2.3 <2.3.2-p1

## Details
A SQL injection vulnerability exists in Magento 2.2 prior to 2.2.10, Magento 2.3 prior to 2.3.3 or 2.3.2-p1. A user with marketing privileges can execute arbitrary SQL queries in the database when accessing email template variables.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-8134
- https://github.com/FriendsOfPHP/security-advisories/blob/master/magento/product-community-edition/CVE-2019-8134.yaml
- https://github.com/magento/magento2
- https://magento.com/security/patches/magento-2.3.3-and-2.2.10-security-update
