# [H] @arikusi/deepseek-mcp-server has an Authorization Bypass Through User-Controlled Key

## Summary
Severity: High
Advisory: CVE-2026-55604
Aliases: GHSA-fh3r-g96v-f578
CVSS: 8.6 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:L)
Published: 2026-07-09
Source: https://osv.dev/vulnerability/CVE-2026-55604
Type: osv

## Details
DeepSeek MCP Server is an MCP server for DeepSeek V4. Starting in version 1.4.2 and prior to version 1.7.0, the process-global `SessionStore` accepts caller-supplied `session_id` values without binding them to any authenticated principal or transport session. An attacker can enumerate active session IDs via `deepseek_sessions`, then reuse a victim-controlled `session_id` in `deepseek_chat` to retrieve and continue the victim's conversation context. Version 1.7.0 contains a patch.

## References
- https://github.com/arikusi/deepseek-mcp-server/releases/tag/v1.7.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/55xxx/CVE-2026-55604.json
- https://github.com/arikusi/deepseek-mcp-server/security/advisories/GHSA-fh3r-g96v-f578
- https://nvd.nist.gov/vuln/detail/CVE-2026-55604
