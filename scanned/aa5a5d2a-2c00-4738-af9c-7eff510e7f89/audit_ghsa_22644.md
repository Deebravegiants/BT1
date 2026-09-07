# [M] paypal/permissions-sdk-php reflected Cross-site Scripting (XSS)

## Summary
Severity: Medium
Advisory: GHSA-2qfv-wwfx-fh34
CVE: CVE-2017-6215
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-2qfv-wwfx-fh34
Type: github-advisory

## Affected
- Packagist: `paypal/permissions-sdk-php` — affected >=0

## Details
paypal/permissions-sdk-php is vulnerable to reflected XSS in the samples/GetAccessToken.php verification_code parameter, resulting in code execution.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-6215
- https://github.com/paypal/permissions-sdk-php/issues/19
- https://github.com/paypal/permissions-sdk-php/commit/a897893d467ca50b9b024b21bd8072ceb3bf2cf8
- https://github.com/paypal/permissions-sdk-php
