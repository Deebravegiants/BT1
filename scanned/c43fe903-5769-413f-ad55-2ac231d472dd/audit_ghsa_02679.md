# [H] Any storage file can be downloaded from p.sh if full server path is known

## Summary
Severity: High
Advisory: GHSA-2rh5-jvgx-pgw3
CWE: CWE-200
Ecosystem: Packagist
Published: 2021-09-14
Source: https://github.com/advisories/GHSA-2rh5-jvgx-pgw3
Type: github-advisory

## Affected
- Packagist: `ezsystems/ezplatform` — affected >=2.0.0 <2.5.24.1
- Packagist: `ezsystems/ezplatform` — affected >=0 <1.13.6.1

## Details
The default configuration for platform.sh (.platform.app.yaml) allows access to uploaded files if you know or can guess their location, regardless of whether roles grant content read access to the content containing those files. If you're using Legacy Bridge, the default configuration also allows access to certain legacy files that should not be readable, including the legacy var directory and extension directories.

## References
- https://github.com/ezsystems/ezplatform/security/advisories/GHSA-2rh5-jvgx-pgw3
- https://developers.ibexa.co/security-advisories/ibexa-sa-2021-006-storage-and-legacy-files-accessible-if-path-is-known
- https://github.com/ezsystems/ezplatform
