# [H] Plane: Cross-workspace asset authorization bypass lets any authenticated user read, copy, delete, and overwrite assets in other Plane workspaces

## Summary
Severity: High
Advisory: CVE-2026-46558
Aliases: GHSA-qw87-v5w3-6vxx
CVSS: 8.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:L)
Published: 2026-06-10
Source: https://osv.dev/vulnerability/CVE-2026-46558
Type: osv

## Details
Plane is an open-source project management tool. Prior to version 1.3.1, there is a cross-workspace asset authorization bypass lets any authenticated user read, copy, delete, and overwrite assets in other Plane workspaces. This issue has been patched in version 1.3.1.

## References
- https://github.com/makeplane/plane/releases/tag/v1.3.1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/46xxx/CVE-2026-46558.json
- https://github.com/makeplane/plane/security/advisories/GHSA-qw87-v5w3-6vxx
- https://nvd.nist.gov/vuln/detail/CVE-2026-46558
