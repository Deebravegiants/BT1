# [M] Browsershot Improper Input Validation vulnerability

## Summary
Severity: Medium
Advisory: GHSA-c9f5-29f6-c35w
CVE: CVE-2024-21549
CWE: CWE-125, CWE-20, CWE-200
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2024-12-20
Source: https://github.com/advisories/GHSA-c9f5-29f6-c35w
Type: github-advisory

## Affected
- Packagist: `spatie/browsershot` — affected >=0 <5.0.3

## Details
Versions of the package spatie/browsershot before 5.0.3 are vulnerable to Improper Input Validation due to improper URL validation through the setUrl method. An attacker can exploit this vulnerability by utilizing view-source:file://, which allows for arbitrary file reading on a local file.

**Note:**

This is a bypass of the fix for [CVE-2024-21544](https://security.snyk.io/vuln/SNYK-PHP-SPATIEBROWSERSHOT-8496745).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-21549
- https://github.com/spatie/browsershot/commit/f791ce0ae8dd99367dbfa30588ee31e1196e1728
- https://github.com/spatie/browsershot
- https://github.com/spatie/browsershot/discussions/906
- https://security.snyk.io/vuln/SNYK-PHP-SPATIEBROWSERSHOT-8533023
