# [H] Claude Code Vulnerable to Command Injection via Piped sed Command Bypasses File Write Restrictions

## Summary
Severity: High
Advisory: GHSA-mhg7-666j-cqg4
CVE: CVE-2026-25723
CWE: CWE-20, CWE-78
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:P/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-02-06
Source: https://github.com/advisories/GHSA-mhg7-666j-cqg4
Type: github-advisory

## Affected
- npm: `@anthropic-ai/claude-code` — affected >=0 <2.0.55

## Details
Claude Code failed to properly validate commands using piped sed operations with the echo command, allowing attackers to bypass file write restrictions. This vulnerability enabled writing to sensitive directories like the .claude folder and paths outside the project scope. Exploiting this required the ability to execute commands through Claude Code with the "accept edits" feature enabled. 

Users on standard Claude Code auto-update received this fix automatically. Users performing manual updates are advised to update to the latest version.

Claude Code thanks hackerone.com/nil221 for reporting this issue!

## References
- https://github.com/anthropics/claude-code/security/advisories/GHSA-mhg7-666j-cqg4
- https://nvd.nist.gov/vuln/detail/CVE-2026-25723
- https://github.com/anthropics/claude-code
