# [M] fuel/core Crypt encryption compromised.

## Summary
Severity: Medium
Advisory: GHSA-fgrx-4637-fcf5
CWE: CWE-327
Ecosystem: Packagist
Published: 2024-05-15
Source: https://github.com/advisories/GHSA-fgrx-4637-fcf5
Type: github-advisory

## Affected
- Packagist: `fuel/core` — affected >=0 <1.8.1

## Details
In fuel/core versions pior to 1.8.1, with the right knowledge, code, and GPU calculation power, Crypt encryption can be broken in minutes.

## References
- https://github.com/fuel/core/commit/59112c96d0a6f2b0ead6a57edd8ac465678bdcb0
- https://fuelphp.com/security-advisories
- https://github.com/FriendsOfPHP/security-advisories/blob/master/fuel/core/2018-04-14-1.yaml
- https://github.com/fuel/core
