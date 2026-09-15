# [H] Filament: Multi-factor authentication (app) can be bypassed when recovery codes are enabled

## Summary
Severity: High
Advisory: GHSA-52xp-w8hr-xv3c
CVE: CVE-2026-77567
CWE: CWE-287
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-09-01
Source: https://github.com/advisories/GHSA-52xp-w8hr-xv3c
Type: github-advisory

## Affected
- Packagist: `filament/filament` — affected >=4.0.0 <4.12.0
- Packagist: `filament/filament` — affected >=5.0.0 <5.7.0

## Details
A flaw in the challenge handling for app-based multi-factor authentication allows the second factor to be bypassed. This issue does not affect email-based MFA. It also only applies when recovery codes are enabled.

## References
- https://github.com/filamentphp/filament/security/advisories/GHSA-52xp-w8hr-xv3c
- https://nvd.nist.gov/vuln/detail/CVE-2026-77567
- https://github.com/filamentphp/filament/commit/45534a6f87f50ac6df3b43680bb33f8da9ef207b
- https://github.com/filamentphp/filament
- https://github.com/filamentphp/filament/releases/tag/v4.12.0
- https://github.com/filamentphp/filament/releases/tag/v5.7.0
