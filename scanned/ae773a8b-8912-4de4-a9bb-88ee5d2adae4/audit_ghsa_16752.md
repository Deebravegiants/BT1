# [M] Insecure State Generation in laravel/socialite

## Summary
Severity: Medium
Advisory: GHSA-h97c-qp24-439v
CWE: CWE-331
Ecosystem: Packagist
Published: 2024-05-15
Source: https://github.com/advisories/GHSA-h97c-qp24-439v
Type: github-advisory

## Affected
- Packagist: `laravel/socialite` — affected >=1.0.0 <2.0.9

## Details
laravel/socialite versions prior to 2.0.9 are found to have an insecure state generation mechanism, potentially exposing the OAuth authentication process to security risks. The issue has been addressed in version 2.0.9 by ensuring that the state is generated using a truly random approach, enhancing the security of the OAuth flow.

## References
- https://github.com/laravel/socialite/pull/91
- https://github.com/laravel/socialite/commit/2ef13bae1484c44ede68e05486bce76cc0fa8dd8
- https://github.com/FriendsOfPHP/security-advisories/blob/master/laravel/socialite/2015-07-23.yaml
- https://github.com/laravel/socialite
