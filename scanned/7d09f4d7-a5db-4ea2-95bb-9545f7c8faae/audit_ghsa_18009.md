# [H] Claude Code's Permissive Default Allowlist Enables Unauthorized File Read and Network Exfiltration in Claude Code

## Summary
Severity: High
Advisory: GHSA-x5gv-jw7f-j6xj
CVE: CVE-2025-55284
CWE: CWE-78
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-08-18
Source: https://github.com/advisories/GHSA-x5gv-jw7f-j6xj
Type: github-advisory

## Affected
- npm: `@anthropic-ai/claude-code` — affected >=0 <1.0.4

## Details
Due to an overly broad allowlist of safe commands, it was possible to bypass the Claude Code confirmation prompts to read a file and then send file contents over the network without user confirmation. Reliably exploiting this requires the ability to add untrusted content into a Claude Code context window. 

Users on standard Claude Code auto-update received this fix automatically after release. Current users of Claude Code are unaffected, as versions prior to 1.0.24 are deprecated and have been forced to update.

Thank you to https://hackerone.com/wunderwuzzi23 for reporting this issue!

## References
- https://github.com/anthropics/claude-code/security/advisories/GHSA-x5gv-jw7f-j6xj
- https://nvd.nist.gov/vuln/detail/CVE-2025-55284
- https://github.com/anthropics/claude-code
