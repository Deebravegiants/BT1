# [M] FastGPT: Stored MCP tool URL SSRF in FastGPT workflow execution

## Summary
Severity: Medium
Advisory: CVE-2026-44284
Aliases: GHSA-cxxj-99f7-f5wq
CVSS: 6.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L)
Published: 2026-05-08
Source: https://osv.dev/vulnerability/CVE-2026-44284
Type: osv

## Details
FastGPT is an AI Agent building platform. Prior to version 4.14.17, FastGPT had an inconsistent SSRF protection gap in MCP tool URL handling. The direct MCP preview/run endpoints already rejected internal/private network URLs, but the MCP tool create/update endpoints could still save an internal MCP server URL. That stored URL could later be used by workflow execution without revalidating the destination. An authenticated user with permission to create or manage MCP toolsets could store an internal endpoint such as http://localhost:3000/mcp and later cause the FastGPT backend workflow runner to connect to that internal destination. This issue has been patched in version 4.14.17.

## References
- https://github.com/labring/FastGPT/releases/tag/v4.14.17
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/44xxx/CVE-2026-44284.json
- https://github.com/labring/FastGPT/security/advisories/GHSA-cxxj-99f7-f5wq
- https://nvd.nist.gov/vuln/detail/CVE-2026-44284
- https://github.com/labring/FastGPT/commit/c1c6b9520d976d25ed945b5bc4e0768149e6db69
- https://github.com/labring/FastGPT/pull/6826
