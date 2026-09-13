# [H] Browsershot Path Traversal

## Summary
Severity: High
Advisory: GHSA-j2gw-r24m-j2qw
CVE: CVE-2025-1022
CWE: CWE-20, CWE-22
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2025-02-05
Source: https://github.com/advisories/GHSA-j2gw-r24m-j2qw
Type: github-advisory

## Affected
- Packagist: `spatie/browsershot` — affected >=0 <5.0.5

## Details
Versions of the package spatie/browsershot before 5.0.5 are vulnerable to Improper Input Validation in the setHtml function, invoked by Browsershot::html(), which can be bypassed by omitting the slashes in the file URI (e.g., file:../../../../etc/passwd). This is due to missing validations of the user input that should be blocking file URI schemes (e.g., file:// and file:/) in the HTML content.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-1022
- https://github.com/spatie/browsershot/commit/bcfd608b264fab654bf78e199bdfbb03e9323eb7
- https://github.com/spatie/browsershot/commit/e3273974506865a24fbb5b65b534d8d4b8dfbf72
- https://gist.github.com/mrdgef/a820837c530e09e1dd725e013e0d4341
- https://github.com/spatie/browsershot
- https://security.snyk.io/vuln/SNYK-PHP-SPATIEBROWSERSHOT-8496747
