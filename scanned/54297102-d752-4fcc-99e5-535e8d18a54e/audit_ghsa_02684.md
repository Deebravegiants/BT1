# [H] User can obtain JWT token even if account is disabled

## Summary
Severity: High
Advisory: GHSA-36mj-6r7r-mqhf
CWE: CWE-284
Ecosystem: Packagist
Published: 2021-09-29
Source: https://github.com/advisories/GHSA-36mj-6r7r-mqhf
Type: github-advisory

## Affected
- Packagist: `ezsystems/ezplatform-rest` — affected >=1.3.0 <1.3.8

## Details
Users can authenticate this way even if their user account is disabled. This is a high risk vulnerability when account disabling is used to block users' access to the system. (Someone who never had an account cannot exploit this vulnerability.) The fix ensures tokens are generated only for enabled user accounts, and is distributed via Composer as ezsystems/ezplatform-rest v1.3.8

## References
- https://github.com/ezsystems/ezplatform-rest/security/advisories/GHSA-36mj-6r7r-mqhf
- https://developers.ibexa.co/security-advisories/ibexa-sa-2021-007-jwt-auth-possible-for-disabled-users.-username-login-handler-can-t-be-disabled
- https://github.com/ezsystems/ezplatform-rest
