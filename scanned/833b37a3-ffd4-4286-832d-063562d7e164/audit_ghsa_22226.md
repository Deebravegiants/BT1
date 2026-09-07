# [H] Magento SQL Injection vulnerability

## Summary
Severity: High
Advisory: GHSA-pf6w-3pfw-fxvw
CVE: CVE-2020-24400
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-pf6w-3pfw-fxvw
Type: github-advisory

## Affected
- Packagist: `magento/community-edition` — affected >=0 <2.3.6
- Packagist: `magento/community-edition` — affected >=2.4.0 <2.4.1

## Details
Magento versions 2.4.0 and 2.3.5 (and earlier) are affected by an SQL Injection vulnerability that could lead to sensitive information disclosure. This vulnerability could be exploited by an authenticated user with permissions to the product listing page to read data from the database.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-24400
- https://github.com/magento/magento2
- https://helpx.adobe.com/security/products/magento/apsb20-59.html
