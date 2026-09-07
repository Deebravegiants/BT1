# [H] Filament: Disabled RichEditor field state can be used for XSS

## Summary
Severity: High
Advisory: GHSA-m9cv-24rx-8mv7
CVE: CVE-2026-55409
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:L/A:N (CVSS_V3)
Published: 2026-06-17
Source: https://github.com/advisories/GHSA-m9cv-24rx-8mv7
Type: github-advisory

## Affected
- Packagist: `filament/forms` — affected >=3.0.0 <3.3.53

## Details
In Filament v3, a disabled `RichEditor` field rendered its raw state without sanitizing HTML. Where the data stored in this field's state isn't sanitized already when the form state was filled, an attacker could plant malicious HTML or JavaScript and achieve XSS that executes for users who view the form.

Please note that Filament v4 and above does not use the same mechanism for rendering a disabled `RichEditor` so this advisory does not apply.

## References
- https://github.com/filamentphp/filament/security/advisories/GHSA-m9cv-24rx-8mv7
- https://github.com/filamentphp/filament/pull/20029
- https://github.com/filamentphp/filament
- https://github.com/filamentphp/filament/releases/tag/v3.3.53
