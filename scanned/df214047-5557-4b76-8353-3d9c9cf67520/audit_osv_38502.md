# [C] Firebird: Path Traversal + Arbitrary File Write Leads to Remote Code Execution

## Summary
Severity: Critical
Advisory: CVE-2026-40342
Aliases: GHSA-7pxc-h3rv-r257
CVSS: 9.9 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-04-17
Source: https://osv.dev/vulnerability/CVE-2026-40342
Type: osv

## Details
Firebird is an open-source relational database management system. In versions prior to 5.0.4, 4.0.7 and 3.0.14, the external engine plugin loader concatenates a user-supplied engine name into a filesystem path without filtering path separators or .. components. An authenticated user with CREATE FUNCTION privileges can use a crafted ENGINE name to load an arbitrary shared library from anywhere on the filesystem via path traversal. The library's initialization code executes immediately during loading, before Firebird validates the module, achieving code execution as the server's OS account. This issue has been fixed in versions 5.0.4, 4.0.7 and 3.0.14.

## References
- https://github.com/FirebirdSQL/firebird/releases/tag/v3.0.14
- https://github.com/FirebirdSQL/firebird/releases/tag/v4.0.7
- https://github.com/FirebirdSQL/firebird/releases/tag/v5.0.4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/40xxx/CVE-2026-40342.json
- https://github.com/FirebirdSQL/firebird/security/advisories/GHSA-7pxc-h3rv-r257
- https://nvd.nist.gov/vuln/detail/CVE-2026-40342
