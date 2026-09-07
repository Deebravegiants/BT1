# [M] z-song laravel-admin XSS via the Slug or Name on the Roles screen

## Summary
Severity: Medium
Advisory: GHSA-fcmh-7492-g4q9
CVE: CVE-2019-17433
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-fcmh-7492-g4q9
Type: github-advisory

## Affected
- Packagist: `encore/laravel-admin` — affected 1.7.3

## Details
z-song laravel-admin 1.7.3 has XSS via the Slug or Name on the Roles screen, because of mishandling on the "Operation log" screen.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-17433
- https://github.com/z-song/laravel-admin/issues/3847
