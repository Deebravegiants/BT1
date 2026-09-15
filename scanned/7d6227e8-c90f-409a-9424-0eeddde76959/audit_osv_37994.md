# [H] Server-Side Request Forgery via MCP Tools Endpoint in FastGPT

## Summary
Severity: High
Advisory: CVE-2026-34163
Aliases: GHSA-x9vj-5m4j-9mfv
CVSS: 7.7 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N)
Published: 2026-03-31
Source: https://osv.dev/vulnerability/CVE-2026-34163
Type: osv

## Details
FastGPT is an AI Agent building platform. Prior to version 4.14.9.5, FastGPT's MCP (Model Context Protocol) tools endpoints (/api/core/app/mcpTools/getTools and /api/core/app/mcpTools/runTool) accept a user-supplied URL parameter and make server-side HTTP requests to it without validating whether the URL points to an internal/private network address. Although the application has a dedicated isInternalAddress() function for SSRF protection (used in other endpoints like the HTTP workflow node), the MCP tools endpoints do not call this function. An authenticated attacker can use these endpoints to scan internal networks, access cloud metadata services, and interact with internal services such as MongoDB and Redis. This issue has been patched in version 4.14.9.5.

## References
- https://github.com/labring/FastGPT/releases/tag/v4.14.9.5
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/34xxx/CVE-2026-34163.json
- https://github.com/labring/FastGPT/security/advisories/GHSA-x9vj-5m4j-9mfv
- https://nvd.nist.gov/vuln/detail/CVE-2026-34163
- https://github.com/labring/FastGPT/commit/bc7eae2ed61481a5e322208829be291faec58c00
- https://github.com/labring/FastGPT/pull/6640
