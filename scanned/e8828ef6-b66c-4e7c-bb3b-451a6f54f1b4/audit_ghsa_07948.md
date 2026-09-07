# [H] Claude Code has a Domain Validation Bypass which Allows Automatic Requests to Attacker-Controlled Domains

## Summary
Severity: High
Advisory: GHSA-vhw5-3g5m-8ggf
CVE: CVE-2026-24052
CWE: CWE-601
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-02-03
Source: https://github.com/advisories/GHSA-vhw5-3g5m-8ggf
Type: github-advisory

## Affected
- npm: `@anthropic-ai/claude-code` — affected >=0 <1.0.111

## Details
Claude Code contained insufficient URL validation in its trusted domain verification mechanism for WebFetch requests. The application used a `startsWith()` function to validate trusted domains (e.g., `docs.python.org`, `modelcontextprotocol.io`), this could have enabled attackers to register domains like `modelcontextprotocol.io.example.com` that would pass validation. This could enable automatic requests to attacker-controlled domains without user consent, potentially leading to data exfiltration. 

Users on standard Claude Code auto-update have received this fix already. Users performing manual updates are advised to update to the latest version.

Thank you to hackerone.com/47sid-praetorian for reporting this issue!

## References
- https://github.com/anthropics/claude-code/security/advisories/GHSA-vhw5-3g5m-8ggf
- https://nvd.nist.gov/vuln/detail/CVE-2026-24052
- https://github.com/anthropics/claude-code
