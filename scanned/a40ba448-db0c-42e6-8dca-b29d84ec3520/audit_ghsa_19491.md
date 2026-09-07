# [M] Laravel Starter Cross Site Scripting (XSS)

## Summary
Severity: Medium
Advisory: GHSA-fpx3-h2pc-88vf
CVE: CVE-2025-26159
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2025-04-22
Source: https://github.com/advisories/GHSA-fpx3-h2pc-88vf
Type: github-advisory

## Affected
- Packagist: `nasirkhan/laravel-starter` — affected >=0 <11.11.0

## Details
Laravel Starter 11.11.0 is vulnerable to Cross Site Scripting (XSS) in the tags feature. Any user with the ability of create or modify tags can inject malicious JavaScript code in the name field.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-26159
- https://github.com/nasirkhan/laravel-starter
- https://godbadtry.github.io/posts/CVE-2025-26159
