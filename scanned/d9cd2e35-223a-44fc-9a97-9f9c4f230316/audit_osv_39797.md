# [H] praisonai-platform: Agent endpoints accept any agent_id without workspace ownership check, cross-workspace read/update/delete IDOR

## Summary
Severity: High
Advisory: CVE-2026-47419
Aliases: GHSA-7p8g-6c6g-h9w7, PYSEC-2026-2931
CVSS: 8.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:L)
Published: 2026-07-21
Source: https://osv.dev/vulnerability/CVE-2026-47419
Type: osv

## Details
PraisonAI Platform is the platform layer for the PraisonAI multi-agent teams system. Versions prior to 0.1.4 have an* Insecure Direct Object Reference. The agent CRUD endpoints (`GET / PATCH / DELETE /workspaces/{workspace_id}/agents/{agent_id}`) gate access on `require_workspace_member(workspace_id)` only, then resolve `agent_id` through `AgentService.get(agent_id)` which is a primary-key lookup with no workspace constraint. A user who is a member of any workspace `W1` can read, modify, or delete agents that belong to a different workspace `W2` by guessing or harvesting an agent UUID and calling `…/workspaces/W1/agents/<W2-agent-id>`. PraisonAI Platform version 0.1.4 patches the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/47xxx/CVE-2026-47419.json
- https://github.com/MervinPraison/PraisonAI/security/advisories/GHSA-7p8g-6c6g-h9w7
- https://nvd.nist.gov/vuln/detail/CVE-2026-47419
- https://github.com/MervinPraison/PraisonAI/commit/ef79b7a0561796ad9807f0f09538c25cc78d3619
