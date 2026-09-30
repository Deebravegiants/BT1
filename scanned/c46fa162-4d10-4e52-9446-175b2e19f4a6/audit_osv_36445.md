# [C] Dive allows One-click Remote Code Execution through Deep Links for MCP Install

## Summary
Severity: Critical
Advisory: CVE-2026-23523
Aliases: GHSA-pjj5-f3wm-f9m8
CVSS: 9.6 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:H)
Published: 2026-01-16
Source: https://osv.dev/vulnerability/CVE-2026-23523
Type: osv

## Details
Dive is an open-source MCP Host Desktop Application that enables integration with function-calling LLMs. Prior to 0.13.0, crafted deeplink can install an attacker-controlled MCP server configuration without sufficient user confirmation and can lead to arbitrary local command execution on the victim’s machine. This vulnerability is fixed in 0.13.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/23xxx/CVE-2026-23523.json
- https://github.com/OpenAgentPlatform/Dive/security/advisories/GHSA-pjj5-f3wm-f9m8
- https://nvd.nist.gov/vuln/detail/CVE-2026-23523
- https://github.com/OpenAgentPlatform/Dive/commit/a5162ac9eff366d8ea1215b8a47139a81a55a779
