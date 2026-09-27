# [H] [Eclipse Theia] Indirect Prompt Injection via Adversarial Workspace File and Directory Names in AI Chat

## Summary
Severity: High
Advisory: GHSA-3jww-hxqj-wfq2
CVE: CVE-2026-44688
CWE: CWE-829
Ecosystem: npm
CVSS: CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:A/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-06-18
Source: https://github.com/advisories/GHSA-3jww-hxqj-wfq2
Type: github-advisory

## Affected
- npm: `@theia/ai-chat-ui` — affected >=0 <1.71.0
- npm: `@theia/ai-chat` — affected >=0 <1.71.0
- npm: `@theia/ai-claude-code` — affected >=0 <1.71.0
- npm: `@theia/ai-code-completion` — affected >=0 <1.71.0
- npm: `@theia/ai-core` — affected >=0 <1.71.0
- npm: `@theia/ai-editor` — affected >=0 <1.71.0
- npm: `@theia/ai-ide` — affected >=0 <1.71.0

## Details
In Eclipse Theia versions prior to 1.71.0, the AI chat agent processed workspace file and directory names as part of its prompt context without distinguishing them from system instructions. An attacker could craft a malicious repository with adversarial directory or file names that, when analyzed by the AI agent, would cause the agent to follow attacker-controlled instructions (indirect prompt injection). Combined with other AI chat features available in untrusted workspaces, this enabled attack chains leading to data exfiltration via Markdown image rendering or arbitrary command execution via task definitions.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-44688
- https://github.com/eclipse-theia/theia/issues/16892
- https://github.com/eclipse-theia/theia/pull/17364
- https://github.com/eclipse-theia/theia/commit/e3fdfe6992389bc5fa611058d00c39d7408508ed
- https://github.com/eclipse-theia/theia
- https://gitlab.eclipse.org/security/cve-assignment/-/work_items/113
