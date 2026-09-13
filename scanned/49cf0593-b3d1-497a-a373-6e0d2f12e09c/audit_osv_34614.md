# [H] FileRise insecure folder visibility via name-based mapping and incomplete ACL checks

## Summary
Severity: High
Advisory: CVE-2025-62510
Aliases: GHSA-jm96-2w52-5qjj
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N)
Published: 2025-10-20
Source: https://osv.dev/vulnerability/CVE-2025-62510
Type: osv

## Details
FileRise is a self-hosted web-based file manager with multi-file upload, editing, and batch operations. In version 1.4.0, a regression allowed folder visibility/ownership to be inferred from folder names. Low-privilege users could see or interact with folders matching their username and, in some cases, other users’ content. This issue has been patched in version 1.5.0, where it introduces explicit per-folder ACLs (owners/read/write/share/read_own) and strict server-side checks across list, read, write, share, rename, copy/move, zip, and WebDAV paths.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/62xxx/CVE-2025-62510.json
- https://github.com/error311/FileRise/security/advisories/GHSA-jm96-2w52-5qjj
- https://nvd.nist.gov/vuln/detail/CVE-2025-62510
- https://github.com/error311/FileRise/issues/55
- https://github.com/error311/FileRise/commit/b6d86b78967baa2f5a1e191903fc4df13998d87f
