# [C] CVE-2025-5277

## Summary
Severity: Critical
Advisory: CVE-2025-5277
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:A/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H)
Published: 2025-05-28
Source: https://osv.dev/vulnerability/CVE-2025-5277
Type: osv

## Details
aws-mcp-server MCP server is vulnerable to command injection. An attacker can craft a prompt that once accessed by the MCP client will run arbitrary commands on the host system.

## References
- https://github.com/alexei-led/aws-mcp-server/blob/94d20ae1798a43ac7e3a28e71900d774e5159c8a/src/aws_mcp_server/cli_executor.py#L92
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/5xxx/CVE-2025-5277.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-5277
- https://github.com/alexei-led/aws-mcp-server/commit/94d20ae1798a43ac7e3a28e71900d774e5159c8a
