# [M] Magento XSS Vulnerability

## Summary
Severity: Medium
Advisory: GHSA-j49x-jjmj-9fqj
CVE: CVE-2019-8227
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-j49x-jjmj-9fqj
Type: github-advisory

## Affected
- Packagist: `magento/core` — affected >=0 <1.9.4.3

## Details
In Magento prior to 1.9.4.3 and Magento prior to 1.14.4.3, an authenticated user with limited administrative privileges can inject arbitrary JavaScript code via import / export functionality when creating profile action XML.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-8227
- https://web.archive.org/web/20211209030216/https://magento.com/security/patches/supee-11219
