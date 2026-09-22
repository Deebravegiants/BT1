# [M] Craft CMS: Authenticated "assets/preview-thumb" discloses signed fallback transform preview link to CP users without asset-view permission

## Summary
Severity: Medium
Advisory: GHSA-x76w-8c62-48mg
CVE: CVE-2026-56384
CWE: CWE-200, CWE-862
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:L/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-07-06
Source: https://github.com/advisories/GHSA-x76w-8c62-48mg
Type: github-advisory

## Affected
- Packagist: `craftcms/cms` — affected >=4.0.0-RC1 <4.17.8
- Packagist: `craftcms/cms` — affected >=5.0.0-RC1 <5.9.14

## Details
### Summary

A user with Control Panel access but without permission to view a target private asset can call `assets/preview-thumb` and receive preview HTML that contains a signed fallback transform link for that private asset.

### Details

Root-cause analysis:
1. The endpoint accepts an attacker-controlled `assetId`.
2. Asset is resolved, and thumbnail HTML is returned.
3. No explicit asset-view permission check is performed before preview generation.

### Impact

Type:

1. Missing authorization
2. Unauthorized preview-link disclosure

  Affected deployments:

1. Craft sites with control panel users who have partial permissions and private assets.

  Security consequence:

  1. A control panel user without asset-view permission can still obtain signed preview transform link data for private assets.
  2. This may increase private asset exposure risk depending on deployment and endpoint chaining.

## Resources

https://github.com/craftcms/cms/commit/d30df3112220db1ffd6726a3ed11857014c7fb27

## References
- https://github.com/craftcms/cms/security/advisories/GHSA-x76w-8c62-48mg
- https://nvd.nist.gov/vuln/detail/CVE-2026-56384
- https://github.com/craftcms/cms/commit/d30df3112220db1ffd6726a3ed11857014c7fb27
- https://github.com/craftcms/cms
- https://www.vulncheck.com/advisories/craft-cms-missing-authorization-in-assets-preview-thumb-endpoint
