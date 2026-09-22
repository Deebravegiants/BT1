# [M] SiYuan before v3.8.1 Path Traversal via asset.upload

## Summary
Severity: Medium
Advisory: CVE-2026-82233
Aliases: GHSA-p23f-cm6q-2qp8
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:P/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-28
Source: https://osv.dev/vulnerability/CVE-2026-82233
Type: osv

## Details
SiYuan before v3.8.1 contains a path traversal vulnerability in the asset.upload MCP tool that accepts arbitrary absolute file paths without workspace boundary validation. Attackers can induce the AI Agent to upload sensitive files such as SSH keys or credentials from outside the workspace into the asset directory through prompt injection.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/82xxx/CVE-2026-82233.json
- https://github.com/siyuan-note/siyuan/security/advisories/GHSA-p23f-cm6q-2qp8
- https://nvd.nist.gov/vuln/detail/CVE-2026-82233
- https://www.vulncheck.com/advisories/siyuan-before-3.8.1-path-traversal-via-asset-upload
