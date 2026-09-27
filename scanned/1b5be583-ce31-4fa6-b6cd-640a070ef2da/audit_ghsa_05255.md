# [H] Filament: Multi-factor authentication (app) recovery codes can still be used multiple times via concurrent submission

## Summary
Severity: High
Advisory: GHSA-mc5j-f6wx-h9qh
CVE: CVE-2026-48505
CWE: CWE-362, CWE-841
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-06-25
Source: https://github.com/advisories/GHSA-mc5j-f6wx-h9qh
Type: github-advisory

## Affected
- Packagist: `filament/filament` — affected >=4.0.0 <4.11.5
- Packagist: `filament/filament` — affected >=5.0.0 <5.6.5

## Details
A flaw in the handling of recovery codes for **app-based multi-factor authentication** allows the same recovery code to be reused via concurrent submission. This issue does **not** affect email-based MFA. It also only applies when recovery codes are enabled.

If an attacker gains access to both the user's password and their recovery codes, they get two authenticated sessions per recovery code burned instead of one, or more if they batch the parallel submissions wider, materially extending the attacker's window of access compared to what the single-use guarantee implies.

## References
- https://github.com/filamentphp/filament/security/advisories/GHSA-mc5j-f6wx-h9qh
- https://nvd.nist.gov/vuln/detail/CVE-2026-48505
- https://github.com/filamentphp/filament
