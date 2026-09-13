# [M] WeKan Board Export REST Endpoints: NULL Pointer Dereference on Invalid authToken Leads to Uncaught Exception / Remote Denial of Service

## Summary
Severity: Medium
Advisory: CVE-2026-68901
Aliases: GHSA-3gcg-g6rf-w2rx
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-08-19
Source: https://osv.dev/vulnerability/CVE-2026-68901
Type: osv

## Details
Wekan is open source kanban built with Meteor. Prior to 10.38, the /api/boards/:boardId/export, /api/boards/:boardId/attachments/:attachmentId/export, /api/boards/:boardId/export/csv, and /api/boards/:boardId/exportExcel handlers in models/export.js and models/exportExcel.js looked up a user from the attacker-controlled authToken query parameter and immediately called user._id.toString() without checking whether ReactiveCache.getUser() returned undefined. A request for a private board with an unknown token therefore threw a TypeError from an asynchronous route, producing an unhandled rejection that could terminate the Wekan process and deny service to all users. Version 10.38 adds a 401 guard after every export token lookup and wraps export handlers with safeRoute() so unexpected exceptions become controlled responses. This issue is fixed in version 10.38.

## References
- https://github.com/wekan/wekan/releases/tag/v10.38
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68901.json
- https://github.com/wekan/wekan/security/advisories/GHSA-3gcg-g6rf-w2rx
- https://nvd.nist.gov/vuln/detail/CVE-2026-68901
- https://github.com/wekan/wekan/commit/40de1799aed7c31494579659850578691171d895
