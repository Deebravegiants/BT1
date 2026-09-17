# [H] Claude Code Research Preview has a Path Restriction Bypass which could allow unauthorized file access

## Summary
Severity: High
Advisory: GHSA-pmw4-pwvc-3hx2
CVE: CVE-2025-54794
CWE: CWE-22
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:P/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-08-04
Source: https://github.com/advisories/GHSA-pmw4-pwvc-3hx2
Type: github-advisory

## Affected
- npm: `@anthropic-ai/claude-code` — affected >=0 <0.2.111

## Details
Due to a path validation flaw using prefix matching instead of canonical path comparison, it was possible to bypass directory restrictions and access files outside the CWD. Successful exploitation depends on the presence of (or ability to create) a directory with the same prefix as the CWD and the ability to add untrusted content into a Claude Code context window. 

Users on standard Claude Code auto-update received this fix automatically after release. Current users of Claude Code are unaffected, as versions prior to 1.0.24 are deprecated and have been forced to update.

Thank you to Elad Beber (Cymulate) for reporting this issue!

## References
- https://github.com/anthropics/claude-code/security/advisories/GHSA-pmw4-pwvc-3hx2
- https://nvd.nist.gov/vuln/detail/CVE-2025-54794
- https://github.com/anthropics/claude-code
