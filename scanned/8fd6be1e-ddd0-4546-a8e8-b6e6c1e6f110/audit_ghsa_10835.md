# [M] AWS API MCP File Access Restriction Bypass

## Summary
Severity: Medium
Advisory: GHSA-2cpp-j2fc-qhp7
CVE: CVE-2026-4270
CWE: CWE-424
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-03-17
Source: https://github.com/advisories/GHSA-2cpp-j2fc-qhp7
Type: github-advisory

## Affected
- PyPI: `awslabs.aws-api-mcp-server` — affected >=0.2.14 <1.3.9
- PyPI: `awslabs-aws-api-mcp-server` — affected >=0.2.14 <1.3.9

## Details
### Description

The AWS API MCP Server is an open source Model Context Protocol (MCP) server that enables AI assistants to interact with AWS services and resources through AWS CLI commands. It provides programmatic access to manage your AWS infrastructure while maintaining proper security controls.

This server acts as a bridge between AI assistants and AWS services, allowing you to create, update, and manage AWS resources across all available services. The server includes a configurable file access feature that controls how AWS CLI commands interact with the local file system. By default, file operations are restricted to a designated working directory (workdir), but this can be configured to allow unrestricted file system access (unrestricted) or to block all local file path arguments entirely (no-access).

**Description:** Improper Protection of Alternate Path exists in the no-access and workdir feature of the AWS API MCP Server versions >= 0.2.14 and < 1.3.9 on all platforms may allow the bypass of intended file access restriction and expose arbitrary local file contents in the MCP client application context.

To remediate this issue, users should upgrade to version 1.3.9.

## References
- https://github.com/awslabs/mcp/security/advisories/GHSA-2cpp-j2fc-qhp7
- https://nvd.nist.gov/vuln/detail/CVE-2026-4270
- https://aws.amazon.com/security/security-bulletins/2026-007-AWS
- https://github.com/awslabs/mcp
- https://github.com/pypa/advisory-database/tree/main/vulns/awslabs-aws-api-mcp-server/PYSEC-2026-162.yaml
- https://pypi.org/project/awslabs.aws-api-mcp-server/1.3.9
