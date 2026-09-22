# [M] JumpServer: KoKo Web Terminal SFTP Path Traversal on Authorized Asset

## Summary
Severity: Medium
Advisory: CVE-2026-54336
Aliases: GHSA-x6rg-36j6-76vr
CVSS: 5.4 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N)
Published: 2026-08-17
Source: https://osv.dev/vulnerability/CVE-2026-54336
Type: osv

## Details
JumpServer is an open source bastion host and an operation and maintenance security audit system. From 4.8.0 until 4.10.17, an authenticated user with SFTP permission to an authorized asset can submit crafted traversal paths through the KoKo Web Terminal SFTP feature, causing AssetDir.GetRealPath() in pkg/srvconn/sftp_asset.go to resolve paths outside the intended SFTP root and permit read, list, write, rename, or delete operations under the configured backend account on that asset. This issue is fixed in version 4.10.17.

## References
- https://github.com/jumpserver/koko/releases/tag/v4.10.17
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/54xxx/CVE-2026-54336.json
- https://github.com/jumpserver/jumpserver/security/advisories/GHSA-x6rg-36j6-76vr
- https://nvd.nist.gov/vuln/detail/CVE-2026-54336
- https://github.com/jumpserver/koko/commit/02fabebe27dacce89114fba122c667a946fd12ea
