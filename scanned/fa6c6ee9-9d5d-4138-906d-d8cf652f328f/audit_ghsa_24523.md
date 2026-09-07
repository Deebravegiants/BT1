# [M] paypal/adaptivepayments-sdk-php vulnerable to a reflected XSS

## Summary
Severity: Medium
Advisory: GHSA-9r4x-3534-w3f9
CVE: CVE-2017-6217
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-9r4x-3534-w3f9
Type: github-advisory

## Affected
- Packagist: `paypal/adaptivepayments-sdk-php` — affected >=0

## Details
paypal/adaptivepayments-sdk-php v3.9.2 is vulnerable to a reflected XSS in the SetPaymentOptions.php resulting code execution

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-6217
- https://github.com/paypal/adaptivepayments-sdk-php/issues/87
- https://github.com/paypal/adaptivepayments-sdk-php
