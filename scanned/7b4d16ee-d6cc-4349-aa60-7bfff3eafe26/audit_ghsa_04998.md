# [M] Claude Code: Out-of-Band Data Exfiltration via Pre-Approved HuggingFace Domain in WebFetch

## Summary
Severity: Medium
Advisory: GHSA-fg94-h982-f3mm
CVE: CVE-2026-54316
CWE: CWE-183, CWE-200, CWE-515
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-06-17
Source: https://github.com/advisories/GHSA-fg94-h982-f3mm
Type: github-advisory

## Affected
- npm: `@anthropic-ai/claude-code` — affected >=0.2.54 <2.1.163

## Details
Because the hostname huggingface.co was pre-approved as a bare hostname for the WebFetch tool, any path on that domain—including attacker-controlled model repositories—was auto-approved without a permission prompt or being subject to --allowedTools restrictions. An attacker able to inject untrusted content into a Claude Code context could direct it to issue WebFetch requests against attacker-controlled repository files (e.g. /resolve/main/config.json), which HuggingFace counts as downloads server-side, creating a covert out-of-band channel for encoding and exfiltrating data Claude can access such as files, environment variables, or command output. Reliably exploiting this required the ability to add untrusted content into a Claude Code context window. Users on standard Claude Code auto-update have received this fix already; users performing manual updates are advised to update to the latest version.

Thank you to hackerone.com/novee for reporting this issue.

## References
- https://github.com/anthropics/claude-code/security/advisories/GHSA-fg94-h982-f3mm
- https://nvd.nist.gov/vuln/detail/CVE-2026-54316
- https://github.com/anthropics/claude-code
