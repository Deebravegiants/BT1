# [M] Snipe-IT has Multi-Tenancy Bypass via Bulk Asset Update

## Summary
Severity: Medium
Advisory: GHSA-33g4-646g-qwmm
CVE: CVE-2026-55482
CWE: CWE-639
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2026-06-23
Source: https://github.com/advisories/GHSA-33g4-646g-qwmm
Type: github-advisory

## Affected
- Packagist: `snipe/snipe-it` — affected >=0 <8.4.2

## Details
### Impact
The `BulkAssetsController::update()` method accepts `company_id` directly from user input without calling `Company::getIdForCurrentUser()`, the standard company-scoping function used by every other controller in the codebase. A non-superadmin user can move assets across company boundaries, breaking multi-tenancy isolation.

### Patches
Patched in https://github.com/grokability/snipe-it/commit/d58fda626e8febfeff4cabbc20ba03edfc411e18

## References
- https://github.com/grokability/snipe-it/security/advisories/GHSA-33g4-646g-qwmm
- https://github.com/grokability/snipe-it/commit/d58fda626e8febfeff4cabbc20ba03edfc411e18
- https://github.com/grokability/snipe-it
