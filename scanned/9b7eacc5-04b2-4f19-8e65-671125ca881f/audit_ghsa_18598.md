# [M] ibexa/user login enumerates user accounts

## Summary
Severity: Medium
Advisory: GHSA-q3x8-6898-23g3
CWE: CWE-209
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:L/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-10-17
Source: https://github.com/advisories/GHSA-q3x8-6898-23g3
Type: github-advisory

## Affected
- Packagist: `ibexa/user` — affected >=5.0.0 <5.0.3

## Details
### Impact
In v5, error messages could provide enough information to tell whether a user exists or not. This is resolved by ensuring the error messages are sufficiently ambigious.

### Patches
See "Patched versions".

### Workarounds
None.

### Resources
https://developers.ibexa.co/security-advisories/ibexa-sa-2025-004-xss-and-enumeration-vulnerabilities-in-back-office

## References
- https://github.com/ibexa/user/security/advisories/GHSA-q3x8-6898-23g3
- https://developers.ibexa.co/security-advisories/ibexa-sa-2025-004-xss-and-enumeration-vulnerabilities-in-back-office
- https://github.com/ibexa/user
