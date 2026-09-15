# [C] Ruflo: Unauthenticated RCE in MCP bridge default docker-compose deployment

## Summary
Severity: Critical
Advisory: CVE-2026-59726
Aliases: GHSA-c4hm-4h84-2cf3
CVSS: 10.0 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-07-09
Source: https://osv.dev/vulnerability/CVE-2026-59726
Type: osv

## Details
Ruflo is an agent meta-harness for Claude Code and Codex. Prior to 3.16.3, ruflo's default docker-compose deployment exposed the MCP bridge POST /mcp and POST /mcp/:group endpoints without authentication, allowing an unauthenticated network attacker to invoke tools/call to terminal_execute, obtain a shell in the bridge container, read provider API keys, and poison AgentDB learning-store patterns. This issue is fixed in version 3.16.3.

## References
- https://github.com/ruvnet/ruflo/releases/tag/v3.16.3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/59xxx/CVE-2026-59726.json
- https://github.com/ruvnet/ruflo/security/advisories/GHSA-c4hm-4h84-2cf3
- https://nvd.nist.gov/vuln/detail/CVE-2026-59726
- https://github.com/ruvnet/ruflo/commit/d00a0a40cd8bdbca877ac7f675f416bdc69accd1
- https://github.com/ruvnet/ruflo/pull/2521
