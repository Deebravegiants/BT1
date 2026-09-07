# [H] Filament Unvalidated Range and Values summarizer values can be used for XSS

## Summary
Severity: High
Advisory: GHSA-vv3x-j2x5-36jc
CVE: CVE-2026-33080
CWE: CWE-79, CWE-80
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-03-18
Source: https://github.com/advisories/GHSA-vv3x-j2x5-36jc
Type: github-advisory

## Affected
- Packagist: `filament/tables` — affected >=4.0.0 <4.8.5
- Packagist: `filament/tables` — affected >=5.0.0 <5.3.5

## Details
Two Table summarizers (`Range`, `Values`) render raw database values without escaping HTML. If there is a lack of validation for the data in the columns that use these summarizers, an attacker could plant malicious HTML / JavaScript and achieve stored XSS that executes for users who view the table with those summarizers.

## References
- https://github.com/filamentphp/filament/security/advisories/GHSA-vv3x-j2x5-36jc
- https://nvd.nist.gov/vuln/detail/CVE-2026-33080
- https://github.com/filamentphp/filament/commit/efa041aeeb4b1a99acd48aaa05584993c926d1ed
- https://github.com/filamentphp/filament
- https://github.com/filamentphp/filament/releases/tag/v4.8.5
- https://github.com/filamentphp/filament/releases/tag/v5.3.5
