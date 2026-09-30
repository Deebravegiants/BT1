# [H] Claude Code vulnerable to arbitrary code execution caused by maliciously configured git email 

## Summary
Severity: High
Advisory: GHSA-j4h9-wv2m-wrf7
CVE: CVE-2025-59041
CWE: CWE-78, CWE-94
Ecosystem: npm
CVSS: CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:P/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-09-10
Source: https://github.com/advisories/GHSA-j4h9-wv2m-wrf7
Type: github-advisory

## Affected
- npm: `@anthropic-ai/claude-code` — affected >=0 <1.0.105

## Details
At startup, Claude Code constructed a shell command that interpolated the value of `git config user.email` from the current workspace. If an attacker controlled the repository’s Git config (e.g., via a malicious `.git/config`) and set `user.email` to a crafted payload, the unescaped interpolation could trigger arbitrary command execution **before** the user accepted the workspace-trust dialog. The issue affects versions prior to `1.0.105`. The fix in `1.0.105` avoids executing commands built from untrusted configuration and properly validates/escapes inputs.

*   **Patches:** Update to `@anthropic-ai/claude-code` `1.0.105` or later.
*   **Workarounds:** Open only trusted workspaces and inspect repository `.git/config` before launch; avoid inheriting untrusted Git configuration values.

> Thank you to the NVIDIA AI Red Team for reporting this issue!

## References
- https://github.com/anthropics/claude-code/security/advisories/GHSA-j4h9-wv2m-wrf7
- https://nvd.nist.gov/vuln/detail/CVE-2025-59041
- https://github.com/anthropics/claude-code
- https://www.npmjs.com/package/@anthropic-ai/claude-code/v/1.0.105
