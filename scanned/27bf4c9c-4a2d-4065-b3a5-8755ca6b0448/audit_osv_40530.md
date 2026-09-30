# [H] Wekan: Missing authorization on OIDC Meteor methods allows privilege escalation to admin

## Summary
Severity: High
Advisory: CVE-2026-53444
Aliases: GHSA-cv95-8h7c-2ffq
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:H/VI:H/VA:L/SC:N/SI:N/SA:N)
Published: 2026-07-15
Source: https://osv.dev/vulnerability/CVE-2026-53444
Type: osv

## Details
Wekan is open source kanban built with Meteor. Prior to 9.32, Wekan OIDC-related Meteor methods in packages/wekan-oidc/oidc_server.js, server/models/org.js, and server/models/team.js are globally callable without the admin authorization checks used by their non-OIDC counterparts. Authenticated users can call setCreateOrgFromOidc, setOrgAllFieldsFromOidc, setCreateTeamFromOidc, setTeamAllFieldsFromOidc, boardRoutineOnLogin, or groupRoutineOnLogin to create or modify organizations and teams, and groupRoutineOnLogin can grant global admin privileges when PROPAGATE_OIDC_DATA is enabled. This issue is fixed in version 9.32.

## References
- https://github.com/wekan/wekan/releases/tag/v9.32
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53444.json
- https://github.com/wekan/wekan/security/advisories/GHSA-cv95-8h7c-2ffq
- https://nvd.nist.gov/vuln/detail/CVE-2026-53444
- https://github.com/wekan/wekan/commit/305864f0c77456ad0f2c1e616266c8a06749c951
