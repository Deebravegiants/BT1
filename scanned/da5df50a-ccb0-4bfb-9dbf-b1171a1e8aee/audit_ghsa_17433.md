# [M] mcp-server-git's unrestricted git_init tool allows repository creation at arbitrary filesystem locations

## Summary
Severity: Medium
Advisory: GHSA-5cgr-j3jf-jw3v
CVE: CVE-2025-68143
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:N/VI:N/VA:N/SC:H/SI:H/SA:H (CVSS_V4)
Published: 2025-12-17
Source: https://github.com/advisories/GHSA-5cgr-j3jf-jw3v
Type: github-advisory

## Affected
- PyPI: `mcp-server-git` — affected >=0 <2025.9.25

## Details
In mcp-server-git versions prior to 2025.9.25, the git_init tool accepted arbitrary filesystem paths and created Git repositories without validating the target location. Unlike other tools which required an existing repository, git_init could operate on any directory accessible to the server process, making those directories eligible for subsequent git operations. The tool was removed entirely, as the server is intended to operate on existing repositories only. Users are advised to upgrade to 2025.9.25 or newer to remediate this issue.

Thank you to https://hackerone.com/yardenporat for disclosure, @0dd for contributing the fix.

## References
- https://github.com/modelcontextprotocol/servers/security/advisories/GHSA-5cgr-j3jf-jw3v
- https://nvd.nist.gov/vuln/detail/CVE-2025-68143
- https://github.com/modelcontextprotocol/servers/commit/eac56e7bcde48fb64d5a973924d05d69a7d876e6
- https://github.com/modelcontextprotocol/servers
