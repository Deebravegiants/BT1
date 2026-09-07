# [M] October CMS has Safe Mode Bypass via CSS Preprocessor Compilers

## Summary
Severity: Medium
Advisory: GHSA-3888-q23f-x7qh
CVE: CVE-2026-26067
CWE: CWE-184, CWE-200, CWE-22
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-04-21
Source: https://github.com/advisories/GHSA-3888-q23f-x7qh
Type: github-advisory

## Affected
- Packagist: `october/system` — affected >=0 <3.7.14
- Packagist: `october/system` — affected >=4.0.0 <4.1.10

## Details
A server-side information disclosure vulnerability was identified in the handling of CSS preprocessor files. Backend users with Editor permissions could craft `.less`, `.sass`, or `.scss` files that leverage the compiler's import functionality to read arbitrary files from the server. This worked even with `cms.safe_mode` enabled.

### Impact
- Potential exposure of sensitive server-side files
- Requires authenticated backend access with Editor permissions
- Only relevant when `cms.safe_mode` is enabled (otherwise direct PHP injection is already possible)

### Patches
The vulnerability has been patched in v3.7.14 and v4.1.10. When `cms.safe_mode` is enabled, `.less`, `.sass`, and `.scss` files can no longer be created, uploaded, or edited across the CMS editor, media manager, and file upload interfaces. All users are encouraged to upgrade to the latest patched version.

### Workarounds
If upgrading immediately is not possible:
- Set `cms.editable_asset_types` config to `['css', 'js']` to remove preprocessor file types from the editor
- Restrict Editor tool access to fully trusted administrators only

- Reported by [Chris Alupului](https://github.com/neosprings)

## References
- https://github.com/octobercms/october/security/advisories/GHSA-3888-q23f-x7qh
- https://nvd.nist.gov/vuln/detail/CVE-2026-26067
- https://github.com/octobercms/october
