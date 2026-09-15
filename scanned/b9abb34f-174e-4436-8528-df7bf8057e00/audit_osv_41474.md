# [M] PraisonAI Platform before 0.1.9 Authorization Bypass via PATCH

## Summary
Severity: Medium
Advisory: CVE-2026-61442
Aliases: GHSA-c78w-2q4r-68r7
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:H/VA:L/SC:N/SI:N/SA:N)
Published: 2026-07-11
Source: https://osv.dev/vulnerability/CVE-2026-61442
Type: osv

## Details
PraisonAI Platform (praisonai-platform) before 0.1.9 fails to enforce owner/admin authorization on the PATCH routes for projects, issues, and agents, which only require workspace-member role. A workspace member can modify owner-created records; for projects, a member can reassign lead_id to their own user id and then delete the owner-created project, bypassing the delete route's owner/admin permission check.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/61xxx/CVE-2026-61442.json
- https://github.com/MervinPraison/PraisonAI/security/advisories/GHSA-c78w-2q4r-68r7
- https://nvd.nist.gov/vuln/detail/CVE-2026-61442
- https://www.vulncheck.com/advisories/praisonai-platform-before-authorization-bypass-via-patch
- https://github.com/MervinPraison/PraisonAI/commit/846568c7a5d8ce9e71e56e4c213f027c04909753
