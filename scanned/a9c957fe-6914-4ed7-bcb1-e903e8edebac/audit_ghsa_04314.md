# [M] Filament has inconsistent scope enforcement for its AttachAction and AssociateAction Select fields

## Summary
Severity: Medium
Advisory: GHSA-7q3w-xqjw-g3cr
CVE: CVE-2026-48067
CWE: CWE-639
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2026-06-11
Source: https://github.com/advisories/GHSA-7q3w-xqjw-g3cr
Type: github-advisory

## Affected
- Packagist: `filament/tables` — affected >=3.0.0 <3.3.51
- Packagist: `filament/actions` — affected >=4.0.0 <4.11.4
- Packagist: `filament/actions` — affected >=5.0.0 <5.6.4

## Details
The `recordSelectOptionsQuery()` method may be used to scope the options available in the `Select` field for `AttachAction` and `AssociateAction`. However, the built-in validation rule for these fields did not apply the same scope. As a result, a user who can trigger these actions could tamper with the Livewire component's state and submit an out-of-scope value.

## References
- https://github.com/filamentphp/filament/security/advisories/GHSA-7q3w-xqjw-g3cr
- https://nvd.nist.gov/vuln/detail/CVE-2026-48067
- https://github.com/filamentphp/filament
- https://github.com/filamentphp/filament/releases/tag/v3.3.51
- https://github.com/filamentphp/filament/releases/tag/v4.11.4
- https://github.com/filamentphp/filament/releases/tag/v5.6.4
