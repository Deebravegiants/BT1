# [H] Claude Code echo command allowed bypass of user approval prompt for command execution

## Summary
Severity: High
Advisory: GHSA-x56v-x2h6-7j34
CVE: CVE-2025-54795
CWE: CWE-78
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-08-04
Source: https://github.com/advisories/GHSA-x56v-x2h6-7j34
Type: github-advisory

## Affected
- npm: `@anthropic-ai/claude-code` — affected >=0 <1.0.20

## Details
Due to an error in command parsing, it was possible to bypass the Claude Code confirmation prompt to trigger execution of an untrusted command. Reliably exploiting this requires the ability to add untrusted content into a Claude Code context window. 

Users on standard Claude Code auto-update received this fix automatically after release. Current users of Claude Code are unaffected, as versions prior to 1.0.24 are deprecated and have been forced to update.

Thank you to Elad Beber (Cymulate) for reporting this issue!

## References
- https://github.com/anthropics/claude-code/security/advisories/GHSA-x56v-x2h6-7j34
- https://nvd.nist.gov/vuln/detail/CVE-2025-54795
- https://github.com/anthropics/claude-code
