# [H] Improper Input Validation in Laravel

## Summary
Severity: High
Advisory: GHSA-w68r-5p45-5rqp
CVE: CVE-2020-24941
CWE: CWE-863
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2021-05-06
Source: https://github.com/advisories/GHSA-w68r-5p45-5rqp
Type: github-advisory

## Affected
- Packagist: `laravel/framework` — affected >=0 <6.18.35
- Packagist: `laravel/framework` — affected >=7.0.0 <7.24.0

## Details
An issue was discovered in Laravel before 6.18.35 and 7.x before 7.24.0. The $guarded property is mishandled in some situations involving requests with JSON column nesting expressions.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-24941
- https://github.com/laravel/framework/commit/897d107775737a958dbd0b2f3ea37877c7526371
- https://blog.laravel.com/security-release-laravel-61835-7240
