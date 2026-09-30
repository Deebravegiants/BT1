# [M] PraisonAI Platform before 0.1.9 Authorization Bypass via Label Endpoints

## Summary
Severity: Medium
Advisory: CVE-2026-61440
Aliases: GHSA-xxgv-vgvj-qvxh
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-07-15
Source: https://osv.dev/vulnerability/CVE-2026-61440
Type: osv

## Details
PraisonAI Platform before 0.1.9 fails to properly authorize label and issue-label mutations, allowing workspace members to rename and recolor shared labels and add or remove labels on owner-created issues. Attackers with workspace member privileges can exploit PATCH and POST/DELETE endpoints to alter shared label taxonomy and manipulate issue-label associations without owner or admin authorization.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/61xxx/CVE-2026-61440.json
- https://github.com/MervinPraison/PraisonAI/security/advisories/GHSA-xxgv-vgvj-qvxh
- https://nvd.nist.gov/vuln/detail/CVE-2026-61440
- https://www.vulncheck.com/advisories/praisonai-platform-before-authorization-bypass-via-label-endpoints
- https://github.com/MervinPraison/PraisonAI/commit/846568c7a5d8ce9e71e56e4c213f027c04909753
