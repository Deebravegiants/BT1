# [H] PraisonAI has Cross-Workspace IDOR and Privilege Escalation via Platform API

## Summary
Severity: High
Advisory: CVE-2026-48169
Aliases: GHSA-gv23-xrm3-8c62, PYSEC-2026-2935
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-07
Source: https://osv.dev/vulnerability/CVE-2026-48169
Type: osv

## Details
PraisonAI is a multi-agent teams system. Versions prior to 0.1.4 of the PraisonAI Platform API have two authorization failures that together break workspace isolation. The service layer for issues and projects performs global primary-key lookups without checking workspace ownership, so any authenticated user can read, modify, and delete resources in any workspace just by swapping UUIDs in their API requests. On top of that, every member management endpoint (add, update role, remove) only requires `min_role="member"`, which lets any workspace member promote themselves to owner and kick out the original owner. A low-privilege member of one workspace can steal data from every other workspace and take over any workspace they belong to. Both issues come from the same gap: the route layer pulls `workspace_id` from the URL and verifies membership, but the service layer ignores the workspace scope for resource lookups and ignores the caller's role level for member operations. The `require_workspace_member()` dependency does its job correctly. The problem is that the service layer doesn't use the information it provides. Version 0.1.4 of the PraisonAI Platform API patch the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/48xxx/CVE-2026-48169.json
- https://github.com/MervinPraison/PraisonAI/security/advisories/GHSA-gv23-xrm3-8c62
- https://github.com/pypa/advisory-database/tree/main/vulns/praisonai-platform/PYSEC-2026-2935.yaml
- https://nvd.nist.gov/vuln/detail/CVE-2026-48169
