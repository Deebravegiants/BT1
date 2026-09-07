# [M] PrestaShop Stored Cross-Site Scripting Vulnerability

## Summary
Severity: Medium
Advisory: GHSA-crpg-2mm2-jjqf
CVE: CVE-2013-4791
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-05
Source: https://github.com/advisories/GHSA-crpg-2mm2-jjqf
Type: github-advisory

## Affected
- Packagist: `prestashop/prestashop` — affected >=0 <1.4.11

## Details
PrestaShop before 1.4.11 allows Logistician, translators and other low level profiles/accounts to inject a persistent XSS vector on TinyMCE.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2013-4791
- https://github.com/PrestaShop/PrestaShop
- http://davidsopaslabs.blogspot.com/2013/07/prestashop-persistent-xss-and-csrf.html
