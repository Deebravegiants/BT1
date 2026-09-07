# [H] Multi-Factor Authentication issue in Laravel Fortify

## Summary
Severity: High
Advisory: GHSA-6w4v-qr4m-97gg
CVE: CVE-2022-25838
CWE: CWE-294
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-02-25
Source: https://github.com/advisories/GHSA-6w4v-qr4m-97gg
Type: github-advisory

## Affected
- Packagist: `laravel/fortify` — affected >=0 <1.11.1

## Details
Laravel Fortify before 1.11.1 allows reuse within a short time window, thus calling into question the "OT" part of the "TOTP" concept.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-25838
- https://github.com/laravel/fortify/issues/201
- https://github.com/laravel/fortify/issues/201#issuecomment-1009282153
- https://github.com/laravel/fortify/pull/357
- https://github.com/laravel/fortify/pull/358
- https://github.com/FriendsOfPHP/security-advisories/blob/master/laravel/fortify/CVE-2022-25838.yaml
- https://github.com/advisories/GHSA-6w4v-qr4m-97gg
- https://github.com/laravel/fortify
