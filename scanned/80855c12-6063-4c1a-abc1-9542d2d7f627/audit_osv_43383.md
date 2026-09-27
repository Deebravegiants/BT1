# [H] File Browser before v2.63.22 Authorization Bypass via Recursive Operations

## Summary
Severity: High
Advisory: CVE-2026-73612
Aliases: GHSA-77x8-73f4-5485
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-13
Source: https://osv.dev/vulnerability/CVE-2026-73612
Type: osv

## Details
File Browser before v2.63.22 fails to validate access rules for descendants during recursive copy, rename, and delete operations, allowing authenticated users to bypass path-based access controls. Attackers can copy, rename, or delete denied files by operating on their allowed parent directory, defeating rule-based isolation for confidentiality and integrity.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/73xxx/CVE-2026-73612.json
- https://github.com/filebrowser/filebrowser/security/advisories/GHSA-77x8-73f4-5485
- https://nvd.nist.gov/vuln/detail/CVE-2026-73612
- https://www.vulncheck.com/advisories/file-browser-before-authorization-bypass-via-recursive-operations
- https://github.com/filebrowser/filebrowser/commit/72faf6dd3c85628e332d3e567124b86708ce2695
