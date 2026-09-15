# [M] State Guessing Vulnerability in laravel/socialite

## Summary
Severity: Medium
Advisory: GHSA-7fjv-25q9-2w88
Ecosystem: Packagist
Published: 2024-05-15
Source: https://github.com/advisories/GHSA-7fjv-25q9-2w88
Type: github-advisory

## Affected
- Packagist: `laravel/socialite` — affected >=1.0.0 <2.0.10

## Details
laravel/socialite versions prior to 2.0.10 are susceptible to a security vulnerability related to state guessing during OAuth authentication. This vulnerability could potentially lead to session hijacking, allowing attackers to compromise user sessions. The issue has been addressed and fixed in version 2.0.10.

## References
- https://github.com/laravel/socialite/pull/93
- https://github.com/laravel/socialite/commit/3d9ed9f4703de82a89541e2458f64de348a60a99
- https://github.com/FriendsOfPHP/security-advisories/blob/master/laravel/socialite/2015-08-03.yaml
- https://github.com/laravel/socialite
