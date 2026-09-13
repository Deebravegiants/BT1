# [M] Statamic: Missing file upload validation on frontend forms allows uploading disallowed file types

## Summary
Severity: Medium
Advisory: GHSA-qhr7-v3xp-vw9m
CVE: CVE-2026-71434
CWE: CWE-434
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2026-08-06
Source: https://github.com/advisories/GHSA-qhr7-v3xp-vw9m
Type: github-advisory

## Affected
- Packagist: `statamic/cms` — affected >=0 <5.74.3
- Packagist: `statamic/cms` — affected >=6.0.0 <6.24.2

## Details
### Impact
Public frontend forms did not enforce the file upload restrictions that the Control Panel enforces, so an unauthenticated visitor could upload file types an administrator had intended to disallow through a form's `assets` or `files` field. For `assets` fields, files could be stored on a public, web-accessible disk. Statamic's global upload allowlist still applied, so executable types such
as `.php` and `.html` remained blocked.


### Patches
This has been fixed in 5.74.3 and 6.24.2.

## References
- https://github.com/statamic/cms/security/advisories/GHSA-qhr7-v3xp-vw9m
- https://github.com/statamic/cms/pull/14958
- https://github.com/statamic/cms/commit/8be7b6c961536d3173ec4e0965d17b1cf820b7ae
- https://github.com/statamic/cms
- https://github.com/statamic/cms/releases/tag/v5.74.3
- https://github.com/statamic/cms/releases/tag/v6.24.2
