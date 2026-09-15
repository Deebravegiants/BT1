# [M] mcp-server-git has missing path validation when using --repository flag

## Summary
Severity: Medium
Advisory: GHSA-j22h-9j4x-23w5
CVE: CVE-2025-68145
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:N/VI:N/VA:N/SC:H/SI:H/SA:N (CVSS_V4)
Published: 2025-12-17
Source: https://github.com/advisories/GHSA-j22h-9j4x-23w5
Type: github-advisory

## Affected
- PyPI: `mcp-server-git` — affected >=0 <2025.12.18

## Details
In mcp-server-git versions prior to 2025.12.18, when the server is started with the --repository flag to restrict operations to a specific repository path, it did not validate that repo_path arguments in subsequent tool calls were actually within that configured path. This could allow tool calls to operate on other repositories accessible to the server process. The fix adds path validation that resolves both the configured repository and the requested path (following symlinks) and verifies the requested path is within the allowed repository before executing any git operations. Users are advised to upgrade to 2025.12.18 to remediate this issue.

Thank you to https://hackerone.com/yardenporat for reporting.

## References
- https://github.com/modelcontextprotocol/servers/security/advisories/GHSA-j22h-9j4x-23w5
- https://nvd.nist.gov/vuln/detail/CVE-2025-68145
- https://github.com/modelcontextprotocol/servers
