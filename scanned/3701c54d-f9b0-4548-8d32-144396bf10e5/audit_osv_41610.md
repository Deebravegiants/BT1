# [M] listmonk: SQL Injection in `/api/subscribers/export` bypasses table access control, leaking admin password hashes and SMTP credentials

## Summary
Severity: Medium
Advisory: CVE-2026-62361
Aliases: GHSA-xgjr-7j9q-2h4r
CVSS: 5.5 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:L/A:N)
Published: 2026-07-15
Source: https://osv.dev/vulnerability/CVE-2026-62361
Type: osv

## Details
listmonk is a standalone, self-hosted, newsletter and mailing list manager. Prior to 6.2.0, listmonk’s GET /api/subscribers/export endpoint injects the user-controlled query parameter into QuerySubscribersForExport in internal/core/subscribers.go without calling validateQueryTables, unlike GET /api/subscribers, allowing an authenticated user with subscribers:sql_query and subscribers:get_all to read arbitrary database tables such as users and settings and execute data-modifying PostgreSQL CTEs. This issue is fixed in version 6.2.0.

## References
- https://github.com/knadh/listmonk/releases/tag/v6.2.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/62xxx/CVE-2026-62361.json
- https://github.com/knadh/listmonk/security/advisories/GHSA-xgjr-7j9q-2h4r
- https://nvd.nist.gov/vuln/detail/CVE-2026-62361
- https://github.com/knadh/listmonk/commit/c0a6525009a65265230185f16e8674dcc83aa024
