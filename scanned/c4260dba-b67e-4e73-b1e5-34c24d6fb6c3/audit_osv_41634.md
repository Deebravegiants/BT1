# [C] Omnigent: Shared Agent Bundle Overwrite Leads to Authenticated Runner RCE

## Summary
Severity: Critical
Advisory: CVE-2026-62674
Aliases: GHSA-jrrm-9hc7-2v3h, PYSEC-2026-3874
CVSS: 9.0 (CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:H/A:H)
Published: 2026-08-21
Source: https://osv.dev/vulnerability/CVE-2026-62674
Type: osv

## Details
Omnigent is an open-source AI agent framework and meta-harness for orchestrating coding agents. Prior to 0.3.0, PUT /sessions/{session_id}/agent checks LEVEL_EDIT permission for a session but does not reject a bound shared or template agent whose agent.session_id is None. An authenticated user with edit access to a session can replace that shared agent bundle through omnigent/server/routes/sessions.py, add a stdio MCP server, and cause later sessions that use the shared agent to launch an attacker-controlled command through omnigent/tools/mcp.py. The command executes with the Omnigent runner process permissions and can expose files, credentials, workspace data, internal services, and runner availability. This issue is fixed in version 0.3.0.

## References
- https://github.com/omnigent-ai/omnigent/releases/tag/v0.3.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/62xxx/CVE-2026-62674.json
- https://github.com/omnigent-ai/omnigent/security/advisories/GHSA-jrrm-9hc7-2v3h
- https://nvd.nist.gov/vuln/detail/CVE-2026-62674
- https://github.com/omnigent-ai/omnigent/commit/25a22dc9e6da4648d23749f0a589e47e6aed991b
- https://github.com/omnigent-ai/omnigent/pull/1418
