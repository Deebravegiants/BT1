# [H] TypeBot: Cross-Workspace Theme Template IDOR (Modification and Deletion)

## Summary
Severity: High
Advisory: CVE-2026-48759
Aliases: GHSA-qv4p-4mp3-pvpv
CVSS: 7.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:L)
Published: 2026-06-17
Source: https://osv.dev/vulnerability/CVE-2026-48759
Type: osv

## Details
TypeBot is a chatbot builder tool. Versions 3.15.2 and below have an Insecure Direct Object Reference vulnerability through cross-workspace Theme Template modification and deletion. The handleSaveThemeTemplate and handleDeleteThemeTemplate handlers validate that the authenticated user is a non-guest member of the provided workspaceId, but then operate on themeTemplateId via Prisma queries that do NOT include workspaceId in the WHERE clause. This allows any authenticated user to modify or delete theme templates belonging to any other workspace and may expose Template IDs via shared typebots or network traffic. This issue has been fixed in version 3.16.0.

## References
- https://github.com/baptisteArno/typebot.io/releases/tag/v3.16.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/48xxx/CVE-2026-48759.json
- https://github.com/baptisteArno/typebot.io/security/advisories/GHSA-qv4p-4mp3-pvpv
- https://nvd.nist.gov/vuln/detail/CVE-2026-48759
