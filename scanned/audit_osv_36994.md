# [M] Plane Vulnerable to Cross-Workspace/Cross-Project Asset Modification via IDOR in ProjectAssetEndpoint.patch

## Summary
Severity: Medium
Advisory: CVE-2026-27705
Aliases: GHSA-rfj3-8c85-g46j
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N/E:U)
Published: 2026-02-25
Source: https://osv.dev/vulnerability/CVE-2026-27705
Type: osv

## Details
Plane is an an open-source project management tool. Prior to version 1.2.2, the `ProjectAssetEndpoint.patch()` method in `apps/api/plane/app/views/asset/v2.py` (lines 579–593) performs a global asset lookup using only the asset ID (`pk`) via `FileAsset.objects.get(id=pk)`, without verifying that the asset belongs to the workspace and project specified in the URL path. This allows any authenticated user (including those with the GUEST role) to modify the `attributes` and `is_uploaded` status of assets belonging to any workspace or project in the entire Plane instance by guessing or enumerating asset UUIDs. Version 1.2.2 fixes the issue.

## References
- https://github.com/makeplane/plane/releases/tag/v1.2.2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/27xxx/CVE-2026-27705.json
- https://github.com/makeplane/plane/security/advisories/GHSA-rfj3-8c85-g46j
- https://nvd.nist.gov/vuln/detail/CVE-2026-27705
- https://github.com/makeplane/plane/commit/9070acbbe81bc02db5c169789da6862d5fc35d96
