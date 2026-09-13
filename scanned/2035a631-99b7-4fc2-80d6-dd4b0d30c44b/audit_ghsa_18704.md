# [M] Jenkins MCP Server Plugin does not perform permission checks in multiple MCP tools

## Summary
Severity: Medium
Advisory: GHSA-mrpq-9jr3-rqq9
CVE: CVE-2025-64132
CWE: CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2025-10-29
Source: https://github.com/advisories/GHSA-mrpq-9jr3-rqq9
Type: github-advisory

## Affected
- Maven: `io.jenkins.plugins:mcp-server` — affected >=0 <0.86.v7d3355e6a

## Details
Jenkins MCP Server Plugin 0.84.v50ca_24ef83f2 and earlier does not perform permission checks in several MCP tools.

This allows to do the following:

- Attackers with Item/Read permission can obtain information about the configured SCM in a job despite lacking Item/Extended Read permission (`getJobScm`).

- Attackers with Item/Read permission can trigger new builds of a job despite lacking Item/Build permission (`triggerBuild`).

- Attackers without Overall/Read permission can retrieve the names of configured clouds (`getStatus`).

MCP Server Plugin 0.86.v7d3355e6a_a_18 performs permission checks for the affected MCP tools.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-64132
- https://github.com/jenkinsci/mcp-server-plugin/commit/59de6a268b4c6844a3a9c6c55a541de183e71a97
- https://github.com/jenkinsci/mcp-server-plugin
- https://www.jenkins.io/security/advisory/2025-10-29/#SECURITY-3622
- http://www.openwall.com/lists/oss-security/2025/10/29/2
