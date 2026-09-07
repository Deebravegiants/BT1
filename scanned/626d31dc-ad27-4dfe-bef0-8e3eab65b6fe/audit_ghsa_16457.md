# [C] Laravel RCE vulnerability in "cookie" session driver

## Summary
Severity: Critical
Advisory: GHSA-2ffv-r4r9-r8xr
CWE: CWE-94
Ecosystem: Packagist
Published: 2024-05-15
Source: https://github.com/advisories/GHSA-2ffv-r4r9-r8xr
Type: github-advisory

## Affected
- Packagist: `illuminate/cookie` — affected >=4.1.0 <6.18.31
- Packagist: `illuminate/cookie` — affected >=7.0.0 <7.22.4

## Details
Application's using the "cookie" session driver were the primary applications affected by this vulnerability. Since we have not yet released a security release for the Laravel 5.5 version of the framework, we recommend that all applications running Laravel 5.5 and earlier do not use the "cookie" session driver in their production deployments.

Regarding the vulnerability, applications using the "cookie" session driver that were also exposing an encryption oracle via their application were vulnerable to remote code execution. An encryption oracle is a mechanism where arbitrary user input is encrypted and the encrypted string is later displayed or exposed to the user. This combination of scenarios lets the user generate valid Laravel signed encryption strings for any plain-text string, thus allowing them to craft Laravel session payloads when an application is using the "cookie" driver.

This fix prefixes cookie values with an HMAC hash of the cookie's name before encryption and then verifies a matching hash on decryption, making it impossible to craft a valid cookie payload even if an encryption oracle is exposed via the application.

## References
- https://blog.laravel.com/laravel-cookie-security-releases
- https://github.com/FriendsOfPHP/security-advisories/blob/master/illuminate/cookie/2020-07-27-1.yaml
- https://github.com/illuminate/cookie
