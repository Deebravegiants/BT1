# [H] Claude Code Vulnerable to Command Injection via Directory Change Bypasses Write Protection

## Summary
Severity: High
Advisory: GHSA-66q4-vfjg-2qhh
CVE: CVE-2026-25722
CWE: CWE-20, CWE-78
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:P/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-02-06
Source: https://github.com/advisories/GHSA-66q4-vfjg-2qhh
Type: github-advisory

## Affected
- npm: `@anthropic-ai/claude-code` — affected >=0 <2.0.57

## Details
Claude Code failed to properly validate directory changes when combined with write operations to protected folders. By using the `cd` command to navigate into sensitive directories like `.claude`, it was possible to bypass write protection and create or modify files without user confirmation. Reliably exploiting this required the ability to add untrusted content into a Claude Code context window. 

Users on standard Claude Code auto-update received this fix automatically. Users performing manual updates are advised to update to the latest version.

About
Claude Code thanks hackerone.com/nil221 for reporting this issue!

## References
- https://github.com/anthropics/claude-code/security/advisories/GHSA-66q4-vfjg-2qhh
- https://nvd.nist.gov/vuln/detail/CVE-2026-25722
- https://github.com/anthropics/claude-code
