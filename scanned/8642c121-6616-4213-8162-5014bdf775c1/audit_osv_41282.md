# [M] Wekan: Checklist direct DDP updates can write checklist data into private boards

## Summary
Severity: Medium
Advisory: CVE-2026-59154
Aliases: GHSA-gv8h-5p3p-6hx7
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N)
Published: 2026-07-10
Source: https://osv.dev/vulnerability/CVE-2026-59154
Type: osv

## Details
Wekan is open source kanban built with Meteor. Prior to 9.64, Wekan has a cross-board authorization bypass in the direct Meteor collection allow rules for Checklists and ChecklistItems because updates are authorized only against the current source doc.cardId and do not inspect the destination cardId or boardId in the update modifier, allowing a low-privileged authenticated user with write access to one board and knowledge of a target private card id to create checklist data on an accessible card and move it into a private board where they are not a member. This issue is fixed in version 9.64.

## References
- https://github.com/wekan/wekan/releases/tag/v9.64
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/59xxx/CVE-2026-59154.json
- https://github.com/wekan/wekan/security/advisories/GHSA-gv8h-5p3p-6hx7
- https://nvd.nist.gov/vuln/detail/CVE-2026-59154
- https://github.com/wekan/wekan/commit/b1ca76007b9a295fd029dfefc1a2d1d6f1920835
