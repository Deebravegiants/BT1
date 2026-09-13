# [M] Wekan: Broken access control in the Excel-export route (`/api/boards/:boardId/exportExcel`)

## Summary
Severity: Medium
Advisory: CVE-2026-68559
Aliases: GHSA-mwq8-ccpm-r533
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-08-19
Source: https://osv.dev/vulnerability/CVE-2026-68559
Type: osv

## Details
Wekan is open source kanban built with Meteor. From 9.57 until 9.74, the /api/boards/:boardId/exportExcel route in models/exportExcel.js called the asynchronous exporterExcel.canExport(user) authorization guard from models/server/ExporterExcel.js without awaiting it. The returned Promise was always truthy, so exporterExcel.build(res) ran even when board.isVisibleBy(user) would deny access, allowing any authenticated non-member to download private board card titles, descriptions, lists, swimlanes, members, and metadata. This issue is fixed in version 9.74.

## References
- https://github.com/wekan/wekan/releases/tag/v9.74
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68559.json
- https://github.com/wekan/wekan/security/advisories/GHSA-mwq8-ccpm-r533
- https://nvd.nist.gov/vuln/detail/CVE-2026-68559
- https://github.com/wekan/wekan/commit/7bbd1a3fad5d868fd01d79b5908913e215698e8e
