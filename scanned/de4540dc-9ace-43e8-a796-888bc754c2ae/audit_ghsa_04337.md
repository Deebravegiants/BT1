# [H] [Eclipse Theia] Indirect Prompt Injection via Auto-Loaded Workspace Prompt Template Files in AI Chat

## Summary
Severity: High
Advisory: GHSA-m973-pr9r-hp2w
CVE: CVE-2026-46580
CWE: CWE-829
Ecosystem: npm
CVSS: CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:A/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-06-18
Source: https://github.com/advisories/GHSA-m973-pr9r-hp2w
Type: github-advisory

## Affected
- npm: `@theia/ai-chat-ui` — affected >=0 <1.71.0
- npm: `@theia/ai-chat` — affected >=0 <1.71.0
- npm: `@theia/ai-claude-code` — affected >=0 <1.71.0
- npm: `@theia/ai-code-completion` — affected >=0 <1.71.0
- npm: `@theia/ai-core` — affected >=0 <1.71.0
- npm: `@theia/ai-editor` — affected >=0 <1.71.0

## Details
In Eclipse Theia versions prior to 1.71.0, files matching the pattern .prompts/*.prompttemplate in a workspace were automatically loaded and could override or extend the AI agent's system prompts. An attacker could craft a malicious repository containing prompt template files that, when the workspace was opened in Theia, replaced the AI's system instructions with attacker-controlled content (indirect prompt injection). Combined with other AI chat features available in untrusted workspaces, this enabled attack chains leading to data exfiltration via Markdown image rendering or arbitrary command execution via task definitions.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-46580
- https://github.com/eclipse-theia/theia/issues/16892
- https://github.com/eclipse-theia/theia/pull/17364
- https://github.com/eclipse-theia/theia/commit/e3fdfe6992389bc5fa611058d00c39d7408508ed
- https://github.com/eclipse-theia/theia
- https://gitlab.eclipse.org/security/cve-assignment/-/work_items/114
