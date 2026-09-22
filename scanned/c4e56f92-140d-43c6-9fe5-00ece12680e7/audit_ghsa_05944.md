# [M] Snipe-IT has missing object-level authorization in Kits API

## Summary
Severity: Medium
Advisory: GHSA-crv3-j83j-f3r6
CVE: CVE-2026-55478
CWE: CWE-639
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:L/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-08-28
Source: https://github.com/advisories/GHSA-crv3-j83j-f3r6
Type: github-advisory

## Affected
- Packagist: `snipe/snipe-it` — affected >=0 <8.6.2

## Details
### Impact
The API endpoint for adding a license to a predefined kit (`POST /api/v1/kits/{kit_id}/licenses`) only checks whether the caller can edit kits, but does not perform object-level authorization on the referenced license itself. Because of this, a low-privilege user with only predefined-kit permissions can still bind a license that they should not be allowed to access or manage into a kit.

## References
- https://github.com/grokability/snipe-it/security/advisories/GHSA-crv3-j83j-f3r6
- https://nvd.nist.gov/vuln/detail/CVE-2026-55478
- https://github.com/grokability/snipe-it/commit/0d870d540d27107634f3134e0e7f106b3faa6992
- https://github.com/grokability/snipe-it
- https://github.com/grokability/snipe-it/releases/tag/v8.6.2
