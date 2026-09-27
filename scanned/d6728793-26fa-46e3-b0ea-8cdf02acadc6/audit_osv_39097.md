# [C] DeepChat: Incomplete Fix for CVE-2025-55733 leads to Remote Code Execution via Markdown Links bypassing `isValidExternalUrl`

## Summary
Severity: Critical
Advisory: CVE-2026-43899
Aliases: GHSA-cp8j-jx7q-7r5f
CVSS: 9.6 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:H)
Published: 2026-05-11
Source: https://osv.dev/vulnerability/CVE-2026-43899
Type: osv

## Details
DeepChat is an open-source artificial intelligence agent platform that unifies models, tools, and agents. Prior to v1.0.4-beta.1, An incomplete mitigation for CVE-2025-55733 leaves DeepChat vulnerable to an arbitrary protocol execution bypass (RCE). While the patch correctly restricted api.openExternal() inside the renderer's preload/index.ts script, it structurally neglected to sanitize native Electron pop-up window handlers. An attacker or a compromised AI endpoint returning a Markdown link can trigger a target="_blank" native window interception in tabPresenter.ts, which forwards the malicious URL directly to shell.openExternal(url) and completely bypasses the isValidExternalUrl security boundary. This vulnerability is fixed in v1.0.4-beta.1.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/43xxx/CVE-2026-43899.json
- https://github.com/ThinkInAIXYZ/deepchat/security/advisories/GHSA-cp8j-jx7q-7r5f
- https://nvd.nist.gov/vuln/detail/CVE-2026-43899
