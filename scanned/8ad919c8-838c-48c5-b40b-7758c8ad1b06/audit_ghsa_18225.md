# [H] Claude Code rg vulnerability does not protect against approval prompt bypass

## Summary
Severity: High
Advisory: GHSA-qxfv-fcpc-w36x
CVE: CVE-2025-58764
CWE: CWE-94
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-09-10
Source: https://github.com/advisories/GHSA-qxfv-fcpc-w36x
Type: github-advisory

## Affected
- npm: `@anthropic-ai/claude-code` — affected >=0 <1.0.105

## Details
Due to an error in command parsing, it was possible to bypass the Claude Code confirmation prompt to trigger execution of an untrusted command. Reliably exploiting this requires the ability to add untrusted content into a Claude Code context window.

Users on standard Claude Code auto-update will have received this fix automatically. Users performing manual updates are advised to update to the latest version.

Thank you to the NVIDIA AI Red Team for reporting this issue!

## References
- https://github.com/anthropics/claude-code/security/advisories/GHSA-qxfv-fcpc-w36x
- https://nvd.nist.gov/vuln/detail/CVE-2025-58764
- https://github.com/anthropics/claude-code
