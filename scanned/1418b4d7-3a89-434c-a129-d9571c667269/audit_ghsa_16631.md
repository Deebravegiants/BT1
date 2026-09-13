# [H] Laravel Cookie serialization vulnerability

## Summary
Severity: High
Advisory: GHSA-2867-6rrm-38gr
CWE: CWE-502
Ecosystem: Packagist
Published: 2024-05-15
Source: https://github.com/advisories/GHSA-2867-6rrm-38gr
Type: github-advisory

## Affected
- Packagist: `illuminate/cookie` — affected >=5.5.0 <5.6.30

## Details
Laravel 5.6.30 is a security release of Laravel and is recommended as an immediate upgrade for all users. Laravel 5.6.30 also contains a breaking change to cookie encryption and serialization logic. Refer to [laravel advisory](https://laravel.com/docs/5.6/upgrade#upgrade-5.6.30) for more details and read the notes carefully when upgrading your application.

## References
- https://github.com/FriendsOfPHP/security-advisories/blob/master/illuminate/cookie/2018-08-08-1.yaml
- https://github.com/illuminate/cookie
- https://laravel.com/docs/5.6/upgrade#upgrade-5.6.30
