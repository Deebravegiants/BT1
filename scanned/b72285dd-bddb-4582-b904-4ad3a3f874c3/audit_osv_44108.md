# [H] MCPHub authenticated horizontal IDOR: any non-admin user executes tools on other users' MCP servers (cross-tenant file read + SSRF)

## Summary
Severity: High
Advisory: CVE-2026-79750
Aliases: GHSA-wfqf-hqwq-8wvf
CVSS: 7.7 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N)
Published: 2026-08-31
Source: https://osv.dev/vulnerability/CVE-2026-79750
Type: osv

## Details
MCPHub is a unified hub for centrally managing and dynamically orchestrating multiple MCP servers/APIs into separate endpoints with flexible routing strategies. Prior to version 1.0.30, MCPHub scopes non-admin users to servers they own (list views and config edits enforce ownership), but the tool-execution API does not. Any authenticated non-admin user can invoke tools on MCP servers owned by other users — servers they cannot even see in GET /api/servers. Because connected MCP servers carry real capability (filesystem, HTTP fetch, cloud APIs with the owner's keys), this is cross-tenant compromise: demonstrated arbitrary host file read (/etc/passwd, another user's secrets) and SSRF. This issue has been patched in version 1.0.30.

## References
- https://github.com/samanhappy/mcphub/releases/tag/v1.0.30
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/79xxx/CVE-2026-79750.json
- https://github.com/samanhappy/mcphub/security/advisories/GHSA-wfqf-hqwq-8wvf
- https://nvd.nist.gov/vuln/detail/CVE-2026-79750
