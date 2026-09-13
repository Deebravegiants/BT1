# [C] LibreChat MCP Stdio Remote Command Execution

## Summary
Severity: Critical
Advisory: CVE-2026-22252
Aliases: GHSA-cxhj-j78r-p88f
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-01-12
Source: https://osv.dev/vulnerability/CVE-2026-22252
Type: osv

## Details
LibreChat is a ChatGPT clone with additional features. Prior to v0.8.2-rc2, LibreChat's MCP stdio transport accepts arbitrary commands without validation, allowing any authenticated user to execute shell commands as root inside the container through a single API request. This vulnerability is fixed in v0.8.2-rc2.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/22xxx/CVE-2026-22252.json
- https://github.com/danny-avila/LibreChat/security/advisories/GHSA-cxhj-j78r-p88f
- https://nvd.nist.gov/vuln/detail/CVE-2026-22252
- https://github.com/danny-avila/LibreChat/commit/211b39f3113d4e6ecab84be0a83f4e9c9dea127f
