# [H] Claude Code can execute commands prior to the startup trust dialog 

## Summary
Severity: High
Advisory: GHSA-4fgq-fpq9-mr3g
CVE: CVE-2025-59536
CWE: CWE-94
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-10-03
Source: https://github.com/advisories/GHSA-4fgq-fpq9-mr3g
Type: github-advisory

## Affected
- npm: `@anthropic-ai/claude-code` — affected >=0 <1.0.111

## Details
Due to a bug in the startup trust dialog implementation, Claude Code could be tricked to execute code contained in a project before the user accepted the startup trust dialog. Exploiting this requires a user to start Claude Code in an untrusted directory. 

Users on standard Claude Code auto-update will have received this fix automatically. Users performing manual updates are advised to update to the latest version.

Thank you to https://hackerone.com/avivdon for reporting this issue!

## References
- https://github.com/anthropics/claude-code/security/advisories/GHSA-4fgq-fpq9-mr3g
- https://nvd.nist.gov/vuln/detail/CVE-2025-59536
- https://github.com/anthropics/claude-code
