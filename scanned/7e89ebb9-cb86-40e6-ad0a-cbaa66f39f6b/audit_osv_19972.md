# [C] CVE-2021-28793

## Summary
Severity: Critical
Advisory: CVE-2021-28793
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-04-20
Source: https://osv.dev/vulnerability/CVE-2021-28793
Type: osv

## Details
vscode-restructuredtext before 146.0.0 contains an incorrect access control vulnerability, where a crafted project folder could execute arbitrary binaries via crafted workspace configuration.

## References
- https://github.com/vscode-restructuredtext/vscode-restructuredtext/releases
- https://github.com/vscode-restructuredtext/vscode-restructuredtext/releases/tag/147.0.0
- https://vuln.ryotak.me/advisories/37
- https://github.com/vscode-restructuredtext/vscode-restructuredtext/commit/1dd3e878a5559e3dfe0e48f145c90418b208c5af
