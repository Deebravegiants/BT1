# [M] Claude Code Leaks Data via Malicious Environment Configuration Before Trust Confirmation

## Summary
Severity: Medium
Advisory: GHSA-jh7p-qr78-84p7
CVE: CVE-2026-21852
CWE: CWE-522
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:L/VI:L/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-01-21
Source: https://github.com/advisories/GHSA-jh7p-qr78-84p7
Type: github-advisory

## Affected
- npm: `@anthropic-ai/claude-code` — affected >=0 <2.0.65

## Details
A vulnerability in Claude Code's project-load flow allowed malicious repositories to exfiltrate data including Anthropic API keys before users confirmed trust. If a user started Claude Code in an attacker-controller repository, and the repository included a settings file that set ANTHROPIC_BASE_URL to an attacker-controlled endpoint, Claude Code would issue API requests before showing the trust prompt, including potentially leaking the user's API keys.

Users on standard Claude Code auto-update have received this fix already. Users performing manual updates are advised to update to the latest version.

## References
- https://github.com/anthropics/claude-code/security/advisories/GHSA-jh7p-qr78-84p7
- https://nvd.nist.gov/vuln/detail/CVE-2026-21852
- https://github.com/anthropics/claude-code
