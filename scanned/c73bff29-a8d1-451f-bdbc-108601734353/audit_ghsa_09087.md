# [H] Craft CMS's Missing Volume Permission Check in AssetsController::actionShowInFolder Allows Information Disclosure

## Summary
Severity: High
Advisory: GHSA-33m5-hqp9-97pw
CVE: CVE-2026-44012
CWE: CWE-862
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-05-06
Source: https://github.com/advisories/GHSA-33m5-hqp9-97pw
Type: github-advisory

## Affected
- Packagist: `craftcms/cms` — affected >=5.0.0-RC1 <5.9.18

## Details
## Summary

`AssetsController::actionShowInFolder()` fetches an asset by ID and returns its filename and complete folder hierarchy (including volume handle, volume UID, folder names, folder UIDs, and folder URI paths) without checking whether the requesting user has `viewAssets` or `viewPeerAssets` permission on the asset’s volume. Any authenticated CP user — even one with zero volume permissions — can enumerate asset filenames and the full folder structure of any volume by supplying arbitrary asset IDs.

This follows the exact same incomplete-patch pattern as four GHSAs merged on 2026-02-25 (GHSA-x76w-8c62-48mg, GHSA-vgjg-248p-rfm2, GHSA-5pgf-h923-m958, GHSA-3pvf-vxrv-hh9c), all of which added `requireVolumePermissionByAsset()` + `requirePeerVolumePermissionByAsset()` to sibling AssetsController actions. The `actionShowInFolder` method was introduced thirteen days before the patch wave and was not included in it.

## Details

The vulnerability is in `src/controllers/AssetsController.php` at line 1437. The method:

1. Calls `requireCpRequest()` — verifies the request targets the CP, enforces `accessCp` permission via `Controller::_enforceAllowAnonymous()`, but does NOT enforce any volume-level permission.
2. Fetches any asset by ID with `Asset::findOne($assetId)` — no `editable`/`savable` scope filter, so all assets across all volumes are reachable.
3. Returns sensitive structural data via JSON.

## Impact

- Any authenticated control panel user with only `accessCp` permission can discover the filenames and complete folder structure (names, UIDs, handles, URIs) of assets in volumes they are not authorized to access.
- Sensitive volume structures — private document repositories, confidential media, internal file names — are exposed to any user who can log into the control panel.
- This enables targeted follow-up attacks: an attacker who knows a private asset’s filename and folder path may have other avenues to exfiltrate the actual file.

## Resources

https://github.com/craftcms/cms/commit/e3f3eaab3d85badd713cfc2c24e5f0792ecdb586

## References
- https://github.com/craftcms/cms/security/advisories/GHSA-33m5-hqp9-97pw
- https://nvd.nist.gov/vuln/detail/CVE-2026-44012
- https://github.com/craftcms/cms/commit/e3f3eaab3d85badd713cfc2c24e5f0792ecdb586
- https://github.com/craftcms/cms
