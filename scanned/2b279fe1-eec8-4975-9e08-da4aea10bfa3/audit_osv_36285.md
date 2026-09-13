# [C] 5ire vulnerable to Remote Code Execution (RCE) via ECharts

## Summary
Severity: Critical
Advisory: CVE-2026-22793
Aliases: GHSA-wg3x-7c26-97wj
CVSS: 9.6 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:H)
Published: 2026-01-21
Source: https://osv.dev/vulnerability/CVE-2026-22793
Type: osv

## Details
5ire is a cross-platform desktop artificial intelligence assistant and model context protocol client. Prior to version 0.15.3, an unsafe option parsing vulnerability in the ECharts Markdown plugin allows any user able to submit ECharts code blocks to execute arbitrary JavaScript code in the renderer context. This can lead to Remote Code Execution (RCE) in environments where privileged APIs (such as Electron’s electron.mcp) are exposed, resulting in full compromise of the host system. Version 0.15.3 patches the issue.

## References
- https://github.com/nanbingxyz/5ire/releases/tag/v0.15.3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/22xxx/CVE-2026-22793.json
- https://github.com/nanbingxyz/5ire/security/advisories/GHSA-wg3x-7c26-97wj
- https://nvd.nist.gov/vuln/detail/CVE-2026-22793
