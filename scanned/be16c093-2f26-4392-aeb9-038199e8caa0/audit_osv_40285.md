# [M] Wekan: Read-only board members can create/modify/delete Custom Fields (privilege escalation via read-level authz on write ops)

## Summary
Severity: Medium
Advisory: CVE-2026-52892
Aliases: GHSA-6733-4wgq-8xvr
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N)
Published: 2026-07-15
Source: https://osv.dev/vulnerability/CVE-2026-52892
Type: osv

## Details
Wekan is open source kanban built with Meteor. Prior to 9.32, Wekan REST handlers in server/models/customFields.js use read-level Authentication.checkBoardAccess instead of write-level Authentication.checkBoardWriteAccess for mutating custom-field routes. A read-only board member can call POST, PUT, and DELETE handlers for /api/boards/:boardId/custom-fields and custom-field dropdown items to create, update, or delete board custom fields. This issue is fixed in version 9.32.

## References
- https://github.com/wekan/wekan/releases/tag/v9.32
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/52xxx/CVE-2026-52892.json
- https://github.com/wekan/wekan/security/advisories/GHSA-6733-4wgq-8xvr
- https://nvd.nist.gov/vuln/detail/CVE-2026-52892
- https://github.com/wekan/wekan/commit/70db04a93fedabe40331f21f86e6bdc91625914e
