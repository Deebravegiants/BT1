# [M] Craft CMS: Low-privilege users could read private asset contents when editing an asset (IDOR)

## Summary
Severity: Medium
Advisory: GHSA-3pvf-vxrv-hh9c
CVE: CVE-2026-33158
CWE: CWE-639
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N/E:U (CVSS_V4)
Published: 2026-03-24
Source: https://github.com/advisories/GHSA-3pvf-vxrv-hh9c
Type: github-advisory

## Affected
- Packagist: `craftcms/cms` — affected >=4.0.0-RC1 <4.17.8
- Packagist: `craftcms/cms` — affected >=5.0.0-RC1 <5.9.14

## Details
### Summary

A low-privileged authenticated user can read private asset content by calling `assets/edit-image` with an arbitrary `assetId` that they are not authorized to view.

The endpoint returns image bytes (or a preview redirect) without enforcing a per-asset view authorization check, leading to potential unauthorized disclosure of private files.

### Details

Root cause:
  - A user-controlled object reference (`assetId`) is used to load and return sensitive content.
  - The action does not verify whether the current user is authorized to view that asset.
  - This creates an authenticated IDOR / authorization bypass.

### Impact

- Craft installations where private/non-public assets exist and low-privileged users can authenticate.

## Resources

https://github.com/craftcms/cms/commit/7290d91639e

## References
- https://github.com/craftcms/cms/security/advisories/GHSA-3pvf-vxrv-hh9c
- https://nvd.nist.gov/vuln/detail/CVE-2026-33158
- https://github.com/craftcms/cms/commit/7290d91639e5e3a4f7e221dfbef95c9b77331860
- https://github.com/craftcms/cms
- https://github.com/craftcms/cms/releases/tag/4.17.8
- https://github.com/craftcms/cms/releases/tag/5.9.14
