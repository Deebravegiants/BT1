# [H] Claude Code Vulnerable to Arbitrary Code Execution Due to Insufficient Startup Warning

## Summary
Severity: High
Advisory: GHSA-ph6w-f82w-28w6
CWE: CWE-94
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-09-03
Source: https://github.com/advisories/GHSA-ph6w-f82w-28w6
Type: github-advisory

## Affected
- npm: `@anthropic-ai/claude-code` — affected >=0 <1.0.87

## Details
When Claude Code was started in a new directory, it displayed a warning asking, "Do you trust the files in this folder?". This warning did not properly document that selecting "Yes, proceed" would allow Claude Code to execute files in the folder without additional confirmation. This may not have been clear to a user so we have updated the warning to clarify this functionality. 

Users on standard Claude Code auto-update will have received this fix automatically. Users performing manual updates are advised to update to the latest version.

Thank you to https://hackerone.com/avivdon for reporting this issue!

## References
- https://github.com/anthropics/claude-code/security/advisories/GHSA-ph6w-f82w-28w6
- https://github.com/anthropics/claude-code
