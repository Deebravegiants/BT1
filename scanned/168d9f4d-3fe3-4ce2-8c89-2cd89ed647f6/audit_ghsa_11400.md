# [H] Claude Code has a Workspace Trust Dialog Bypass via Repo-Controlled Settings File

## Summary
Severity: High
Advisory: GHSA-mmgp-wc2j-qcv7
CVE: CVE-2026-33068
CWE: CWE-807
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:P/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-19
Source: https://github.com/advisories/GHSA-mmgp-wc2j-qcv7
Type: github-advisory

## Affected
- npm: `@anthropic-ai/claude-code` — affected >=0 <2.1.53

## Details
Claude Code resolved the permission mode from settings files, including the repo-controlled `.claude/settings.json`, before determining whether to display the workspace trust confirmation dialog. A malicious repository could set `permissions.defaultMode` to `bypassPermissions` in its committed `.claude/settings.json`, causing the trust dialog to be silently skipped on first open. This allowed a user to be placed into a permissive mode without seeing the trust confirmation prompt, making it easier for an attacker-controlled repository to gain tool execution without explicit user consent.

Users on standard Claude Code auto-update have received this fix already. Users performing manual updates are advised to update to the latest version.

Thank you to hackerone.com/cantina_xyz for reporting this issue.

## References
- https://github.com/anthropics/claude-code/security/advisories/GHSA-mmgp-wc2j-qcv7
- https://nvd.nist.gov/vuln/detail/CVE-2026-33068
- https://github.com/anthropics/claude-code
