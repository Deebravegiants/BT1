# [H] Claude Code has a Path Restriction Bypass via ZSH Clobber which Allows Arbitrary File Writes

## Summary
Severity: High
Advisory: GHSA-q728-gf8j-w49r
CVE: CVE-2026-24053
CWE: CWE-22, CWE-78
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:P/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-02-03
Source: https://github.com/advisories/GHSA-q728-gf8j-w49r
Type: github-advisory

## Affected
- npm: `@anthropic-ai/claude-code` — affected >=0 <2.0.74

## Details
Due to a Bash command validation flaw in parsing ZSH clobber syntax, it was possible to bypass directory restrictions and write files outside the current working directory without user permission prompts. Exploiting this required the user to use ZSH and the ability to add untrusted content into a Claude Code context window. 

Users on standard Claude Code auto-update have received this fix already. Users performing manual updates are advised to update to the latest version.

Claude Code thanks https://hackerone.com/alexbernier for reporting this issue!

## References
- https://github.com/anthropics/claude-code/security/advisories/GHSA-q728-gf8j-w49r
- https://nvd.nist.gov/vuln/detail/CVE-2026-24053
- https://github.com/anthropics/claude-code
