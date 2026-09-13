# [M] SSRF via unvalidated attachment URLs in Mattermost Agents plugin MCP server

## Summary
Severity: Medium
Advisory: CVE-2026-4339
CVSS: 6.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N)
Published: 2026-06-26
Source: https://osv.dev/vulnerability/CVE-2026-4339
Type: osv

## Details
Mattermost versions 10.11.x <= 10.11.18, 11.6.x <= 11.6.3, 11.5.x <= 11.5.6 fail to validate attachment URLs against internal or private IP ranges in the Mattermost Agents plugin MCP server which allows an attacker with access to the MCP server in stdio mode to perform server-side request forgery (SSRF) and exfiltrate data from internal network services via supplying internal URLs as file attachments in post creation requests.. Mattermost Advisory ID: MMSA-2026-00635

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/4xxx/CVE-2026-4339.json
- https://mattermost.com/security-updates
- https://nvd.nist.gov/vuln/detail/CVE-2026-4339
