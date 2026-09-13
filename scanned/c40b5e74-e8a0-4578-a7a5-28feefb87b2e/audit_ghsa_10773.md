# [M] OpenClaw: MCP stdio server env could load dangerous startup variables from workspace config

## Summary
Severity: Medium
Advisory: GHSA-mj59-h3q9-ghfh
CVE: CVE-2026-44995
CWE: CWE-427, CWE-454, CWE-829
Ecosystem: npm
CVSS: CVSS:4.0/AV:L/AC:L/AT:P/PR:L/UI:A/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-04-25
Source: https://github.com/advisories/GHSA-mj59-h3q9-ghfh
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.4.20

## Details
## Affected Packages / Versions

- Package: `openclaw` (npm)
- Affected versions: `< 2026.4.20`
- Patched version: `2026.4.20`

## Impact

Workspace MCP stdio configuration could pass dangerous process-startup environment variables such as `NODE_OPTIONS`, `LD_PRELOAD`, or `BASH_ENV` to the spawned MCP server process. In a malicious workspace, this could make the MCP child load attacker-controlled code when the operator starts a session that uses that MCP server.

The impact is limited to local/workspace trust boundaries and requires the operator to run OpenClaw in a workspace containing the malicious MCP configuration. Severity is therefore medium, not high/critical.

## Fix

OpenClaw now filters MCP stdio environment entries through the host environment safety denylist before spawning stdio MCP servers.

Fix commits:

- `62fa5071896e95edc7f67d1cebc70a2859e283af`
- `85d86ebc4bf3d2226d39d132a484f4f7a299fa1b`

## Release

Fixed in OpenClaw `2026.4.20`.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-mj59-h3q9-ghfh
- https://nvd.nist.gov/vuln/detail/CVE-2026-44995
- https://github.com/openclaw/openclaw/commit/62fa5071896e95edc7f67d1cebc70a2859e283af
- https://github.com/openclaw/openclaw/commit/85d86ebc4bf3d2226d39d132a484f4f7a299fa1b
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-arbitrary-code-execution-via-mcp-stdio-environment-variables
