# [H] Auth0 WordPress Plugin has Insufficient Entropy in Cookie Encryption

## Summary
Severity: High
Advisory: GHSA-vfpx-q664-h93m
CWE: CWE-331
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2026-04-03
Source: https://github.com/advisories/GHSA-vfpx-q664-h93m
Type: github-advisory

## Affected
- Packagist: `auth0/wordpress` — affected >=5.0.0-BETA0 <5.6.0

## Details
### Impact
In applications built with the Auth0 PHP SDK, cookies are encrypted with insufficient entropy, which may result in threat actors brute-forcing the encryption key and forging session cookies.

### Am I Affected?
Consumers are affected if their application meets the following preconditions:
- It is using the Auth0 WordPress Plugin, versions between 5.0.0-BETA0 and 5.5.0
- Auth0 WordPress plugin using the Auth0-PHP SDK versions between 8.0.0 to 8.18.0.

### Resolution
Upgrade Auth0/wordpress to version 5.6.0 or greater.

## References
- https://github.com/auth0/wordpress/security/advisories/GHSA-vfpx-q664-h93m
- https://github.com/auth0/wordpress
