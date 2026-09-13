# [M] Shelf: SQL Injection via sortBy Parameter

## Summary
Severity: Medium
Advisory: CVE-2026-44204
Aliases: GHSA-69xv-wmgg-3qp3
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-05-12
Source: https://osv.dev/vulnerability/CVE-2026-44204
Type: osv

## Details
Shelf is a platform for tracking physical assets. From 1.12 to before 1.20.1, a SQL injection vulnerability in the sortBy query parameter on the /assets route allows any authenticated user (any role) to execute arbitrary SQL and read data from any table in the database, including data belonging to other organizations. This vulnerability is fixed in 1.20.1.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/44xxx/CVE-2026-44204.json
- https://github.com/Shelf-nu/shelf.nu/security/advisories/GHSA-69xv-wmgg-3qp3
- https://nvd.nist.gov/vuln/detail/CVE-2026-44204
- https://github.com/Shelf-nu/shelf.nu/commit/5d35c15856dbf267fab4dccafd077ee7a6fa6f40
