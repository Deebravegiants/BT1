# [H] Claude Code Command Validation Bypass Allows Arbitrary Code Execution

## Summary
Severity: High
Advisory: GHSA-xq4m-mc3c-vvg3
CVE: CVE-2025-66032
CWE: CWE-20, CWE-77
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-12-03
Source: https://github.com/advisories/GHSA-xq4m-mc3c-vvg3
Type: github-advisory

## Affected
- npm: `@anthropic-ai/claude-code` — affected >=0 <1.0.93

## Details
Due to errors in parsing shell commands related to $IFS and short CLI flags, it was possible to bypass the Claude Code read-only validation and trigger arbitrary code execution. Reliably exploiting this requires the ability to add untrusted content into a Claude Code context window.

Users on standard Claude Code auto-update have received this fix already. Users performing manual updates are advised to update to the latest version.

Thank you to [RyotaK](hxxps://ryotak.net) from [GMO Flatt Security Inc.](hxxps://flatt.tech/en/) for reporting this issue!

## References
- https://github.com/anthropics/claude-code/security/advisories/GHSA-xq4m-mc3c-vvg3
- https://nvd.nist.gov/vuln/detail/CVE-2025-66032
- https://github.com/anthropics/claude-code
