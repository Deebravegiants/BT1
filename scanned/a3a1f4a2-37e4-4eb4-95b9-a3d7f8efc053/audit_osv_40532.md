# [M] Wekan: `cloneBoard` Meteor method has no authorization check — any user can clone (read) any private board by ID

## Summary
Severity: Medium
Advisory: CVE-2026-53447
Aliases: GHSA-qfqv-42qw-vvwh
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-07-15
Source: https://osv.dev/vulnerability/CVE-2026-53447
Type: osv

## Details
Wekan is open source kanban built with Meteor. Prior to 9.35, the Wekan cloneBoard Meteor method in models/import.js uses caller-supplied sourceBoardId to build a board export through models/exporter.js without invoking canExport() or checking source-board membership. Any authenticated user who knows a private board ID can clone the board into their own account and read its cards, comments, attachments, member information, and activities. This issue is fixed in version 9.35.

## References
- https://github.com/wekan/wekan/releases/tag/v9.35
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53447.json
- https://github.com/wekan/wekan/security/advisories/GHSA-qfqv-42qw-vvwh
- https://nvd.nist.gov/vuln/detail/CVE-2026-53447
- https://github.com/wekan/wekan/commit/357de728c03113b787065bac2c5832ad77f1a117
