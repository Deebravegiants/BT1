# [C] RestDB's Codehooks.io MCP Server Vulnerable to Command Injection

## Summary
Severity: Critical
Advisory: CVE-2025-53100
Aliases: GHSA-fhq6-jf5q-qxvq
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:A/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2025-07-01
Source: https://osv.dev/vulnerability/CVE-2025-53100
Type: osv

## Details
RestDB's Codehooks.io MCP Server is an MCP server on the Codehooks.io platform. Prior to version 0.2.2, the MCP server is written in a way that is vulnerable to command injection attacks as part of some of its MCP Server tools definition and implementation. This could result in a user initiated remote command injection attack on a running MCP Server. This issue has been patched in version 0.2.2.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/53xxx/CVE-2025-53100.json
- https://github.com/RestDB/codehooks-mcp-server/security/advisories/GHSA-fhq6-jf5q-qxvq
- https://nvd.nist.gov/vuln/detail/CVE-2025-53100
- https://github.com/RestDB/codehooks-mcp-server/commit/62f918a6fde6a8c700521b542b85315c70f05794
- https://github.com/RestDB/codehooks-mcp-server/commit/83db1d1b4c856cbe4a1b961d315706198bb0ffb8
