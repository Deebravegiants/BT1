# [M] Filament: Multi-factor authentication (app) codes can still be used after a newer code has been used

## Summary
Severity: Medium
Advisory: GHSA-r3j6-gpjw-qfjr
CVE: CVE-2026-84306
CWE: CWE-294
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2026-09-01
Source: https://github.com/advisories/GHSA-r3j6-gpjw-qfjr
Type: github-advisory

## Affected
- Packagist: `filament/filament` — affected >=4.0.0 <4.12.6
- Packagist: `filament/filament` — affected >=5.0.0 <5.7.6

## Details
A flaw in the handling of one-time codes for app-based multi-factor authentication allows a previously issued code to be used after a newer code has already been accepted. This issue does not affect email-based MFA. Submitting the exact same code twice was already prevented, but any other code within the accepted time window was not.

If an attacker gains access to both the user's password and a single one-time code, that code stays usable for the remainder of its time window, which is around four minutes on the default settings, including after the legitimate user has already logged in with a newer code.

## References
- https://github.com/filamentphp/filament/security/advisories/GHSA-r3j6-gpjw-qfjr
- https://github.com/filamentphp/filament/pull/20335
- https://github.com/filamentphp/filament/commit/b6bde8572bcac75d4f5b4ec892ba7b9e91e0ab4d
- https://github.com/filamentphp/filament
- https://github.com/filamentphp/filament/releases/tag/v4.12.6
- https://github.com/filamentphp/filament/releases/tag/v5.7.6
