# [M] [Eclipse Theia] Data Exfiltration via Markdown Image Rendering in AI Chat

## Summary
Severity: Medium
Advisory: GHSA-qwjm-9c66-w4q4
CVE: CVE-2026-22551
CWE: CWE-201
Ecosystem: npm
CVSS: CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:A/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-06-18
Source: https://github.com/advisories/GHSA-qwjm-9c66-w4q4
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
In Eclipse Theia versions prior to 1.71.0, the AI chat rendered Markdown image tags from AI responses, triggering HTTP requests to arbitrary external URLs without restriction. Combined with prompt injection in a malicious workspace, an attacker could induce the AI agent to construct image URLs encoding sensitive information from the workspace or conversation context, exfiltrating it to attacker-controlled servers. The workspace trust enforcement introduced in v1.71.0 mitigates the documented attack chain by disabling AI features in untrusted workspaces.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-22551
- https://github.com/eclipse-theia/theia/issues/16892
- https://github.com/eclipse-theia/theia/pull/17364
- https://github.com/eclipse-theia/theia/commit/e3fdfe6992389bc5fa611058d00c39d7408508ed
- https://github.com/eclipse-theia/theia
- https://gitlab.eclipse.org/security/cve-assignment/-/work_items/115
