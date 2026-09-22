# [H] Wekan: a low-privilege board member escalates to board admin and takes over a private board via the `sort` collection-allow rule

## Summary
Severity: High
Advisory: CVE-2026-68561
Aliases: GHSA-xm8x-c8wg-jhmf
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-19
Source: https://osv.dev/vulnerability/CVE-2026-68561
Type: osv

## Details
Wekan is open source kanban built with Meteor. Prior to 9.89, the second Boards.allow({ update }) rule in server/permissions/boards.js called canUpdateBoardSort in server/lib/utils.js, which authorized any board member whenever fieldNames included sort. Because Meteor combines allow rules with OR semantics and applies the complete modifier, a comment-only or read-only member could send one Boards.update with $set values for sort, members, permission, and title, make themselves the sole board administrator, expose a private board, and evict the legitimate owner; the last-admin deny rule inspected only $pull and did not block a wholesale $set of members. Version 9.89 requires sort to be the only modified field and rejects $set member arrays that remove the last active administrator. This issue is fixed in version 9.89.

## References
- https://github.com/wekan/wekan/releases/tag/v9.89
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68561.json
- https://github.com/wekan/wekan/security/advisories/GHSA-xm8x-c8wg-jhmf
- https://nvd.nist.gov/vuln/detail/CVE-2026-68561
- https://github.com/wekan/wekan/commit/dc135f6e7d59f9f56065cd5df83b1f123ea120bb
