# [H] FileRise: Path Traversal in `resumableIdentifier` Leading to Arbitrary File Write, Recursive Directory Deletion, and Limited Existence Oracle

## Summary
Severity: High
Advisory: CVE-2026-33329
Aliases: GHSA-c2jm-4wp9-5vrh
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:H)
Published: 2026-03-24
Source: https://osv.dev/vulnerability/CVE-2026-33329
Type: osv

## Details
FileRise is a self-hosted web file manager / WebDAV server. From version 1.0.1 to before version 3.10.0, the resumableIdentifier parameter in the Resumable.js chunked upload handler (UploadModel::handleUpload()) is concatenated directly into filesystem paths without any sanitization. An authenticated user with upload permission can exploit this to write files to arbitrary directories on the server, delete arbitrary directories via the post-assembly cleanup, and probe file/directory existence. This issue has been patched in version 3.10.0.

## References
- https://github.com/error311/FileRise/releases/tag/v3.10.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/33xxx/CVE-2026-33329.json
- https://github.com/error311/FileRise/security/advisories/GHSA-c2jm-4wp9-5vrh
- https://nvd.nist.gov/vuln/detail/CVE-2026-33329
- https://github.com/error311/FileRise/commit/3871f9fd1661688bed4f7dd23912be0ebf50973c
