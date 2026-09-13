# [H] Auth0 laravel-auth0 SDK has Insufficient Entropy in Cookie Encryption

## Summary
Severity: High
Advisory: GHSA-fmg6-246m-9g2v
CWE: CWE-331
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2026-04-03
Source: https://github.com/advisories/GHSA-fmg6-246m-9g2v
Type: github-advisory

## Affected
- Packagist: `auth0/login` — affected >=7.0.0 <7.21.0

## Details
### Impact
In applications built with the Auth0 PHP SDK, cookies are encrypted with insufficient entropy, which may result in threat actors brute-forcing the encryption key and forging session cookies.

### Am I Affected?
You are affected if you meet the following preconditions:

- Applications using laravel-auth0 SDK, versions between 7.0.0 and 7.20.0
- Laravel-auth0 SDK using the Auth0-PHP SDK versions between 8.0.0 to 8.18.0.


### Resolution
Upgrade Auth0/laravel-auth0 to version 7.21.0 or greater.

## References
- https://github.com/auth0/laravel-auth0/security/advisories/GHSA-fmg6-246m-9g2v
- https://github.com/auth0/laravel-auth0
