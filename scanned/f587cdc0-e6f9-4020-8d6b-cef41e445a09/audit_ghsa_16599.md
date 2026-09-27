# [M] Laravel Hijacked authentication cookies vulnerability

## Summary
Severity: Medium
Advisory: GHSA-q4xf-7fw5-4x8v
CWE: CWE-384
Ecosystem: Packagist
Published: 2024-05-15
Source: https://github.com/advisories/GHSA-q4xf-7fw5-4x8v
Type: github-advisory

## Affected
- Packagist: `illuminate/auth` — affected >=4.0.0 <4.1.26

## Details
Laravel 4.1.26 introduces security improvements for "remember me" cookies. Before this update, if a remember cookie was hijacked by another malicious user, the cookie would remain valid for a long period of time, even after the true owner of the account reset their password, logged out, etc.

This change requires the addition of a new remember_token column to your users (or equivalent) database table. After this change, a fresh token will be assigned to the user each time they login to your application. The token will also be refreshed when the user logs out of the application. The implications of this change are: if a "remember me" cookie is hijacked, simply logging out of the application will invalidate the cookie.

## References
- https://github.com/FriendsOfPHP/security-advisories/blob/master/illuminate/auth/2014-04-15.yaml
- https://github.com/illuminate/auth
- https://laravel.com/docs/5.1/upgrade#upgrade-4.1.26
