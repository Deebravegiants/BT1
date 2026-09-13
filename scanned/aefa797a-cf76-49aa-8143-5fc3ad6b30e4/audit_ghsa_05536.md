# [C] terminal-controller-mcp vulnerable to Command Injection

## Summary
Severity: Critical
Advisory: GHSA-h4rf-624j-gj33
CVE: CVE-2025-61492
CWE: CWE-77
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-01-07
Source: https://github.com/advisories/GHSA-h4rf-624j-gj33
Type: github-advisory

## Affected
- PyPI: `terminal-controller` — affected >=0

## Details
A command injection vulnerability in the execute_command function of terminal-controller-mcp 0.1.7 allows attackers to execute arbitrary commands via a crafted input.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-61492
- https://github.com/GongRzhe/terminal-controller-mcp/issues/7
- https://github.com/cfdude/super-shell-mcp/issues/19
- https://github.com/GongRzhe/terminal-controller-mcp
