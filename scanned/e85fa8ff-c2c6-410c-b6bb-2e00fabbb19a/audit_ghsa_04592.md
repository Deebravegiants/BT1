# [M] Filament: Unauthenticated temporary file upload on auth pages

## Summary
Severity: Medium
Advisory: GHSA-44wp-g8f4-f4v5
CVE: CVE-2026-48500
CWE: CWE-862
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:L (CVSS_V3)
Published: 2026-06-23
Source: https://github.com/advisories/GHSA-44wp-g8f4-f4v5
Type: github-advisory

## Affected
- Packagist: `filament/filament` — affected >=4.0.0 <4.11.5
- Packagist: `filament/filament` — affected >=5.0.0 <5.6.5
- Packagist: `filament/filament` — affected >=3.0.0 <3.3.52

## Details
Any schema can contain a file upload form field, so Filament applies Livewire's `WithFileUploads` trait to the Livewire component the schema is embedded in. However, some schemas, such as the panel login form, do not require file uploads, and exposing unauthenticated temporary file uploads on these components is not an acceptable risk. On these components, an unauthenticated attacker could upload arbitrary files to the application's temporary storage, which could be abused to exhaust disk space or inflate storage costs.

## References
- https://github.com/filamentphp/filament/security/advisories/GHSA-44wp-g8f4-f4v5
- https://nvd.nist.gov/vuln/detail/CVE-2026-48500
- https://github.com/filamentphp/filament
