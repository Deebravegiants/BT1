# [M] Wekan: Authorization bypass in copyBoard DDP method allows any user to copy private boards

## Summary
Severity: Medium
Advisory: CVE-2026-53445
Aliases: GHSA-7w2h-g83c-jqrp
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:L/VA:N/SC:N/SI:N/SA:N)
Published: 2026-07-15
Source: https://osv.dev/vulnerability/CVE-2026-53445
Type: osv

## Details
Wekan is open source kanban built with Meteor. Prior to 9.32, the Wekan copyBoard Meteor DDP method in server/publications/boards.js copies a board by caller-supplied board ID without checking this.userId, membership, or admin access. Any authenticated user can copy a private board they are not a member of, including its cards, checklists, custom fields, labels, and rules, while the REST POST /api/boards/:boardId/copy path correctly checks board admin access. This issue is fixed in version 9.32.

## References
- https://github.com/wekan/wekan/releases/tag/v9.32
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53445.json
- https://github.com/wekan/wekan/security/advisories/GHSA-7w2h-g83c-jqrp
- https://nvd.nist.gov/vuln/detail/CVE-2026-53445
- https://github.com/wekan/wekan/commit/8940a103970c5da3f02b3615eef09fabfff421e3
