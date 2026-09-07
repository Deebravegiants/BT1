# [H] Magento authorization bypass vulnerability

## Summary
Severity: High
Advisory: GHSA-8wm7-h2qh-ff4c
CVE: CVE-2020-9587
CWE: CWE-863
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-8wm7-h2qh-ff4c
Type: github-advisory

## Affected
- Packagist: `magento/community-edition` — affected >=0
- Packagist: `magento/community-edition` — affected >=2.3.0 <2.3.4-p2
- Packagist: `magento/core` — affected >=0 <1.9.4.5
- Packagist: `magento/project-community-edition` — affected >=0

## Details
Magento versions 2.3.4 and earlier, 2.2.11 and earlier (see note), 1.14.4.4 and earlier, and 1.9.4.4 and earlier have an authorization bypass vulnerability. Successful exploitation could lead to potentially unauthorized product discounts.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-9587
- https://github.com/magento/magento2
- https://helpx.adobe.com/security/products/magento/apsb20-22.html
