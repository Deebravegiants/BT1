# [H] Claude Code vulnerable to command execution prior to startup trust dialog

## Summary
Severity: High
Advisory: GHSA-5hhx-v7f6-x7gv
CVE: CVE-2025-65099
CWE: CWE-94
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:P/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-11-19
Source: https://github.com/advisories/GHSA-5hhx-v7f6-x7gv
Type: github-advisory

## Affected
- npm: `@anthropic-ai/claude-code` — affected >=0 <1.0.39

## Details
When using Claude Code with Yarn installed, Yarn config files can trigger code execution when running yarn --version. This could lead to a bypass of the directory trust dialog in Claude Code, as plugins and yarnPath could be executed prior to the user accepting the risks of working in an untrusted directory. Users on standard Claude Code auto-update will have received this fix automatically. Users performing manual updates are advised to update to the latest version.

Thank you to Benjamin Faller, Redguard AG and Michael Hess for reporting this issue!

## References
- https://github.com/anthropics/claude-code/security/advisories/GHSA-5hhx-v7f6-x7gv
- https://nvd.nist.gov/vuln/detail/CVE-2025-65099
- https://github.com/anthropics/claude-code
