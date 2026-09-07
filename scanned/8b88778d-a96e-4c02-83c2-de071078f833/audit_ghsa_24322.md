# [M] paypal/invoice-sdk-php reflected XSS

## Summary
Severity: Medium
Advisory: GHSA-626w-hmpw-x74j
CVE: CVE-2017-6213
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-626w-hmpw-x74j
Type: github-advisory

## Affected
- Packagist: `paypal/invoice-sdk-php` — affected >=0

## Details
paypal/invoice-sdk-php is vulnerable to reflected XSS in samples/permissions.php via the permToken parameter, resulting in code execution.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-6213
- https://github.com/paypal/invoice-sdk-php/issues/13
- https://github.com/paypal/invoice-sdk-php
