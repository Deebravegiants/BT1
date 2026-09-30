# [M] OpenList: Authenticated arbitrary file write via Content-Disposition path traversal in SimpleHttp offline-download tool

## Summary
Severity: Medium
Advisory: CVE-2026-75602
Aliases: GHSA-h6cj-26g5-67fv, GO-2026-6368
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:N/I:H/A:H)
Published: 2026-09-03
Source: https://osv.dev/vulnerability/CVE-2026-75602
Type: osv

## Details
OpenList a file list program that supports multiple storage. Prior to 4.2.3, OpenList's offline-download feature at POST /api/fs/add_offline_download with tool: "SimpleHttp" accepts an attacker-supplied URL and saves its bytes under a per-task temporary directory before transferring them to the user's destination storage. The temporary filename comes from the attacker-controlled Content-Disposition header, is passed from parseFilenameFromContentDisposition in internal/offline_download/http/util.go to filepath.Join(task.TempDir, filename) in SimpleHttp.Run in internal/offline_download/http/client.go, and is opened with os.Create without a containment check. Because filepath.Join cleans .. segments, a non-admin user with PermAddOfflineDownload on any path can traverse out of task.TempDir and create, truncate, or overwrite any file writable by the OpenList process whose parent directory already exists. The server/handles/offline_download.go AddOfflineDownload route uses normal user authentication rather than AuthAdmin, and local-storage destinations fall through tryPutUrl in internal/offline_download/tool/add.go to the vulnerable SimpleHttp.Run path. This issue is fixed in version 4.2.3.

## References
- https://github.com/OpenListTeam/OpenList/releases/tag/v4.2.3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/75xxx/CVE-2026-75602.json
- https://github.com/OpenListTeam/OpenList/security/advisories/GHSA-h6cj-26g5-67fv
- https://nvd.nist.gov/vuln/detail/CVE-2026-75602
- https://github.com/OpenListTeam/OpenList/commit/9cc5dd969b9833c8cb4e14c338c3571dfdbe2108
