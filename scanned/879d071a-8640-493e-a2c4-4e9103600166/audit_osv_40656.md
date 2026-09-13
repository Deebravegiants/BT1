# [H] LibreChat: Missing Resource Parameter Validation in MCP OAuth Flow

## Summary
Severity: High
Advisory: CVE-2026-54030
Aliases: GHSA-gvpj-vm2f-2m23
CVSS: 8.0 (CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:C/C:H/I:H/A:N)
Published: 2026-06-25
Source: https://osv.dev/vulnerability/CVE-2026-54030
Type: osv

## Details
LibreChat is an enhanced ChatGPT clone that supports multiple AI providers. Prior to 0.8.5, LibreChat's MCP OAuth implementation does not validate that the resource parameter from OAuth Protected Resource metadata (RFC 9728) matches the configured MCP server URL, allowing a malicious MCP server to steal access tokens intended for a legitimate server. This vulnerability is fixed in 0.8.5.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/54xxx/CVE-2026-54030.json
- https://github.com/danny-avila/LibreChat/security/advisories/GHSA-gvpj-vm2f-2m23
- https://nvd.nist.gov/vuln/detail/CVE-2026-54030
