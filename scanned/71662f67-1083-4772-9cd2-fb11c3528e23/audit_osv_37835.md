# [M] FileRise has incorrect authorization in /api/file/snippet.php allows read_own users to read other users’ file content

## Summary
Severity: Medium
Advisory: CVE-2026-33477
Aliases: GHSA-62wx-vp78-2p83
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2026-03-26
Source: https://osv.dev/vulnerability/CVE-2026-33477
Type: osv

## Details
FileRise is a self-hosted web-based file manager with multi-file upload, editing, and batch operations. In versiosn 2.3.7 through 3.10.0, the file snippet endpoint `/api/file/snippet.php` allows an authenticated user with only `read_own` access to a folder to retrieve snippet content from files uploaded by other users in the same folder. This is a server-side authorization flaw in the `read_own` enforcement for hover previews. Version 3.11.0 fixes the issue.

## References
- https://github.com/error311/FileRise/releases/tag/v3.11.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/33xxx/CVE-2026-33477.json
- https://github.com/error311/FileRise/security/advisories/GHSA-62wx-vp78-2p83
- https://nvd.nist.gov/vuln/detail/CVE-2026-33477
