# [H] Wekan: Broken access control: any authenticated user can move their Cards/Lists/Swimlanes into a private board they are not a member of (cross-board write via collection allow rule)

## Summary
Severity: High
Advisory: CVE-2026-55234
Aliases: GHSA-gm7v-pc38-53jr
CVSS: 8.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:N/I:H/A:L)
Published: 2026-07-15
Source: https://osv.dev/vulnerability/CVE-2026-55234
Type: osv

## Details
Wekan is open source kanban built with Meteor. Prior to 9.37, Wekan DDP update allow rules in server/permissions/cards.js, server/permissions/lists.js, and server/permissions/swimlanes.js authorize against the stored source boardId and do not validate a new boardId in the update modifier. Any authenticated user with write access to their own board can call /cards/update, /lists/update, or /swimlanes/update to move cards, lists, or swimlanes into a private board they are not a member of. This issue is fixed in version 9.37.

## References
- https://github.com/wekan/wekan/releases/tag/v9.37
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/55xxx/CVE-2026-55234.json
- https://github.com/wekan/wekan/security/advisories/GHSA-gm7v-pc38-53jr
- https://nvd.nist.gov/vuln/detail/CVE-2026-55234
- https://github.com/wekan/wekan/commit/d369a3614a4737c29d48a6345a790edf2506ddae
