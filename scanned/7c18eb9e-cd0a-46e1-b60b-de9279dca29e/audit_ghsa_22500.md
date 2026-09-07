# [M] Magento Cross-Site Request Forgery (CSRF)

## Summary
Severity: Medium
Advisory: GHSA-w3mq-67mw-3p9f
CVE: CVE-2018-5301
CWE: CWE-352
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-w3mq-67mw-3p9f
Type: github-advisory

## Affected
- Packagist: `magento/community-edition` — affected >=0 <2.0.10
- Packagist: `magento/community-edition` — affected >=2.1.0 <2.1.2

## Details
Magento Community Edition and Enterprise Edition before 2.0.10 and 2.1.x before 2.1.2 have CSRF resulting in deletion of a customer address from an address book, aka APPSEC-1433.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-5301
- https://github.com/magento/magento2
- https://magento.com/security/patches/magento-2010-and-212-security-update
