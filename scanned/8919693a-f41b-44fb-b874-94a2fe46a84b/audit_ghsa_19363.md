# [M] Laravel Rest Api has a Search Validation Bypass

## Summary
Severity: Medium
Advisory: GHSA-69rh-hccr-cxrj
CVE: CVE-2025-48490
CWE: CWE-1173, CWE-20
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N/E:U (CVSS_V4)
Published: 2025-05-27
Source: https://github.com/advisories/GHSA-69rh-hccr-cxrj
Type: github-advisory

## Affected
- Packagist: `lomkit/laravel-rest-api` — affected >=0 <2.13.0

## Details
A validation bypass vulnerability was discovered  prior to version 2.13.0, where multiple validations defined for the same attribute could be silently overridden. Due to how the framework merged validation rules across multiple contexts (such as index, store, and update actions), malicious actors could exploit this behavior by crafting requests that bypass expected validation rules, potentially injecting unexpected or dangerous parameters into the application.

Impact:

This could lead to unauthorized data being accepted or processed by the API, depending on the context in which the validation was bypassed.

Patch:

The issue was fixed in [PR #172](https://github.com/Lomkit/laravel-rest-api/pull/172) by ensuring that multiple rule definitions are merged correctly rather than overwritten.

## References
- https://github.com/Lomkit/laravel-rest-api/security/advisories/GHSA-69rh-hccr-cxrj
- https://nvd.nist.gov/vuln/detail/CVE-2025-48490
- https://github.com/Lomkit/laravel-rest-api/pull/172
- https://github.com/Lomkit/laravel-rest-api/commit/88b14587b4efd7e59d7379658c606d325bb513b4
- https://github.com/Lomkit/laravel-rest-api
