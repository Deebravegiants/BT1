# [C] TypeBot vulnerable to cross-workspace OAuth credential takeover in updateOAuthCredentials via missing object binding

## Summary
Severity: Critical
Advisory: CVE-2026-48765
Aliases: GHSA-3788-7276-x4j4
CVSS: 9.9 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:L)
Published: 2026-08-11
Source: https://osv.dev/vulnerability/CVE-2026-48765
Type: osv

## Details
TypeBot is a chatbot builder tool. Versions prior to 3.17.0 allow a low-privilege read collaborator to extract a workspace OAuth `credentialsId` from a readable bot configuration and then overwrite that credential through `handleUpdateOAuthCredentials()` by supplying an attacker-controlled writable `workspaceId`. The update path validates only the attacker-supplied workspace and then updates the credential record by global `id` alone, while also rewriting the credential's `workspaceId`. This allows cross-workspace OAuth credential takeover and reassignment. Version 3.17.0 patches the issue.

## References
- https://github.com/baptisteArno/typebot.io/releases/tag/v3.17.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/48xxx/CVE-2026-48765.json
- https://github.com/baptisteArno/typebot.io/security/advisories/GHSA-3788-7276-x4j4
- https://nvd.nist.gov/vuln/detail/CVE-2026-48765
- https://github.com/baptisteArno/typebot.io/commit/7ae4c007d0987d2ca907b47e1b7418db62b8a157
- https://github.com/baptisteArno/typebot.io/pull/2459
