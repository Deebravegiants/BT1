# [C] OpenAI Codex CLI enables code execution through malicious MCP (Model Context Protocol) configuration files

## Summary
Severity: Critical
Advisory: GHSA-xrxf-jgv3-qmrm
CVE: CVE-2025-61260
CWE: CWE-94
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-04-14
Source: https://github.com/advisories/GHSA-xrxf-jgv3-qmrm
Type: github-advisory

## Affected
- npm: `@openai/codex` — affected >=0

## Details
A vulnerability was identified in OpenAI Codex CLI v0.23.0 and before that enables code execution through malicious MCP (Model Context Protocol) configuration files. The attack is triggered when a user runs the codex command inside a malicious or compromised repository. Codex automatically loads project-local .env and .codex/config.toml files without requiring user confirmation, allowing attackers to embed arbitrary commands that execute immediately.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-61260
- https://github.com/openai/codex
- https://research.checkpoint.com/2025/openai-codex-cli-command-injection-vulnerability
- http://openai.com
