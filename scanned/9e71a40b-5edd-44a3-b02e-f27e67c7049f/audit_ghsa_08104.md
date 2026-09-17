# [H] Claude Code has a Command Injection in find Command Bypasses User Approval Prompt

## Summary
Severity: High
Advisory: GHSA-qgqw-h4xq-7w8w
CVE: CVE-2026-24887
CWE: CWE-78, CWE-94
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:P/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-02-03
Source: https://github.com/advisories/GHSA-qgqw-h4xq-7w8w
Type: github-advisory

## Affected
- npm: `@anthropic-ai/claude-code` — affected >=0 <2.0.72

## Details
Due to an error in command parsing, it was possible to bypass the Claude Code confirmation prompt to trigger execution of untrusted commands through the find command. Reliably exploiting this required the ability to add untrusted content into a Claude Code context window. 

Users on standard Claude Code auto-update have received this fix already. Users performing manual updates are advised to update to the latest version.

Claude Code thanks https://hackerone.com/alexbernier for reporting this issue!

## References
- https://github.com/anthropics/claude-code/security/advisories/GHSA-qgqw-h4xq-7w8w
- https://nvd.nist.gov/vuln/detail/CVE-2026-24887
- https://github.com/anthropics/claude-code
