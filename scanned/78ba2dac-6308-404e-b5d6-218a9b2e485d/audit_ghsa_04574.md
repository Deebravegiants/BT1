# [M] Filament: Unvalidated ImageColumn and ImageEntry values can be used for XSS

## Summary
Severity: Medium
Advisory: GHSA-3fc8-8hp6-6jr4
CVE: CVE-2026-48167
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-06-23
Source: https://github.com/advisories/GHSA-3fc8-8hp6-6jr4
Type: github-advisory

## Affected
- Packagist: `filament/infolists` — affected >=4.0.0 <4.11.5
- Packagist: `filament/tables` — affected >=4.0.0 <4.11.5
- Packagist: `filament/infolists` — affected >=5.0.0 <5.6.5
- Packagist: `filament/tables` — affected >=5.0.0 <5.6.5

## Details
The `ImageColumn` and `ImageEntry` components render raw database values without escaping HTML. Where the data passed to these components isn't validated, an attacker could plant malicious HTML or JavaScript and achieve stored XSS that executes for users who view the table or schema.

## References
- https://github.com/filamentphp/filament/security/advisories/GHSA-3fc8-8hp6-6jr4
- https://nvd.nist.gov/vuln/detail/CVE-2026-48167
- https://github.com/filamentphp/filament
