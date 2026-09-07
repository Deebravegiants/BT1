# [C] Login timing attack in ezsystems/ezpublish-kernel

## Summary
Severity: Critical
Advisory: GHSA-xfqg-p48g-hh94
CWE: CWE-208
Ecosystem: Packagist
Published: 2022-06-02
Source: https://github.com/advisories/GHSA-xfqg-p48g-hh94
Type: github-advisory

## Affected
- Packagist: `ezsystems/ezpublish-kernel` — affected >=7.5.0 <7.5.29

## Details
Ibexa DXP is using random execution time to hinder timing attacks against user accounts, a method of discovering whether a given account exists in a system without knowing its password, thus affecting privacy. This implementation was found to not be good enough in some situations. The fix replaces this with constant time functionality, configured in the new security.yml parameter 'ibexa.security.authentication.constant_auth_time'. It will log a warning if the constant time is exceeded. If this happens the setting should be increased.

## References
- https://github.com/ezsystems/ezpublish-kernel/security/advisories/GHSA-xfqg-p48g-hh94
- https://github.com/ezsystems/ezpublish-kernel/commit/913fe17281536a91437d94e8267181ae8b57f5d5
- https://developers.ibexa.co/security-advisories/ibexa-sa-2022-006-vulnerabilities-in-page-builder-login-and-commerce
- https://github.com/ezsystems/ezpublish-kernel
- https://issues.ibexa.co/browse/IBX-1755
