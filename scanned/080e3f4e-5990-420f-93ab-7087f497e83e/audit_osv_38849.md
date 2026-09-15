# [H] jotty·page: Unauthenticated Path Traversal leads to sensitive file disclosure and session-token reuse impact

## Summary
Severity: High
Advisory: CVE-2026-42564
Aliases: GHSA-7843-gwq8-g96f
CVSS: 8.2 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:N)
Published: 2026-05-11
Source: https://osv.dev/vulnerability/CVE-2026-42564
Type: osv

## Details
jotty·page is a self-hosted app for your checklists and notes. Prior to 1.22.0, an unauthenticated path traversal vulnerability exists in /api/app-icons/[filename]. The filename route parameter is joined into a filesystem path without traversal/boundary validation, allowing file reads outside data/uploads/app-icons/. This vulnerability is fixed in 1.22.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/42xxx/CVE-2026-42564.json
- https://github.com/fccview/jotty/security/advisories/GHSA-7843-gwq8-g96f
- https://nvd.nist.gov/vuln/detail/CVE-2026-42564
