# [M] Laravel Cross-site Scripting (XSS) vulnerability in blade templating

## Summary
Severity: Medium
Advisory: GHSA-vr95-p7q6-8m9q
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2024-05-15
Source: https://github.com/advisories/GHSA-vr95-p7q6-8m9q
Type: github-advisory

## Affected
- Packagist: `laravel/framework` — affected >=7.0.0 <7.1.2

## Details
Laravel 7.1.2 addresses a possible XSS related attack vector in the Laravel 7.x Blade Component tag attributes when users are allowed to dictate the value of attributes. All Laravel 7.x users are encouraged to upgrade as soon as possible.

## References
- https://github.com/laravel/framework/pull/31945
- https://blog.laravel.com/security-laravel-712-released
- https://github.com/FriendsOfPHP/security-advisories/blob/master/laravel/framework/2020-03-13-1.yaml
- https://github.com/laravel/framework
- https://github.com/laravel/framework/releases/tag/v7.1.2
