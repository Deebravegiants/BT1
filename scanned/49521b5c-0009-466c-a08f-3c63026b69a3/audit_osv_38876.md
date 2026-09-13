# [H] Flowise: Mass Assignment in Tool Update Endpoint Allows Cross-Workspace Resource Reassignment

## Summary
Severity: High
Advisory: CVE-2026-42862
Aliases: GHSA-x5v6-pj28-cwwm
CVSS: 7.5 (CVSS:4.0/AV:N/AC:H/AT:N/PR:L/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-06-08
Source: https://osv.dev/vulnerability/CVE-2026-42862
Type: osv

## Details
Flowise is a drag & drop user interface to build a customized large language model flow. Prior to version 3.1.2, a mass assignment vulnerability exists in the tool update endpoint of FlowiseAI. The endpoint allows authenticated users to modify server-controlled properties such as workspaceId, createdDate, and updatedDate when updating a tool resource. Due to missing server-side validation and authorization checks, an attacker can manipulate the workspaceId field and reassign tools to arbitrary workspaces. This breaks tenant isolation in multi-workspace environments. This issue has been patched in version 3.1.2.

## References
- https://github.com/FlowiseAI/Flowise/releases/tag/flowise%403.1.2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/42xxx/CVE-2026-42862.json
- https://github.com/FlowiseAI/Flowise/security/advisories/GHSA-x5v6-pj28-cwwm
- https://nvd.nist.gov/vuln/detail/CVE-2026-42862
