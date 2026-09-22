# [H] FileRise improper ownership/permission validation allowed cross-tenant file operations

## Summary
Severity: High
Advisory: CVE-2025-62509
Aliases: GHSA-6p87-q9rh-95wh
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N)
Published: 2025-10-20
Source: https://osv.dev/vulnerability/CVE-2025-62509
Type: osv

## Details
FileRise is a self-hosted web-based file manager with multi-file upload, editing, and batch operations. Prior to version 1.4.0, a business logic flaw in FileRise’s file/folder handling allows low-privilege users to perform unauthorized operations (view/delete/modify) on files created by other users. The root cause was inferring ownership/visibility from folder names (e.g., a folder named after a username) and missing server-side authorization/ownership checks across file operation endpoints. This amounted to an IDOR pattern: an attacker could operate on resources identified only by predictable names. This issue has been patched in version 1.4.0 and further hardened in version 1.5.0. A workaround for this issue involves restricting non-admin users to read-only or disable delete/rename APIs server-side, avoid creating top-level folders named after other usernames, and adding server-side checks that verify ownership before delete/rename/move.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/62xxx/CVE-2025-62509.json
- https://github.com/error311/FileRise/security/advisories/GHSA-6p87-q9rh-95wh
- https://nvd.nist.gov/vuln/detail/CVE-2025-62509
- https://github.com/error311/FileRise/issues/53
- https://github.com/error311/FileRise/commit/25ce6a76beb60950359c0304765ad91a8aff8ad8
