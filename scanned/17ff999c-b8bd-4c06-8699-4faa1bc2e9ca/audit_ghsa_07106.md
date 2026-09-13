# [H] AWS API MCP Server Security Policy Bypass via Startup Initialization Failure

## Summary
Severity: High
Advisory: GHSA-29w2-fq35-v728
CVE: CVE-2026-16584
CWE: CWE-455
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-07-24
Source: https://github.com/advisories/GHSA-29w2-fq35-v728
Type: github-advisory

## Affected
- PyPI: `awslabs.aws-api-mcp-server` — affected >=0.2.13 <1.3.47

## Details
## Summary
The AWS API MCP Server is an open source Model Context Protocol (MCP) server that enables AI assistants to interact with AWS services and resources through AWS CLI commands. It provides programmatic access to manage your AWS infrastructure while maintaining proper security controls. It includes an optional, user-configured security policy that can deny or gate specific AWS operations. An issue exists where, if the data used to enforce this policy fails to initialize at server startup, the per-request policy check is silently skipped for the lifetime of the process.

### Impact
On startup, the server loads data used to enforce the configured security policy. If that load fails, the server continues running without the enforcement data in place. In the default configuration, the per-request security check is then bypassed for the lifetime of the process: configured deny and gate rules are not consulted, and AWS API operations the policy was intended to restrict execute without enforcement. The scope is limited to the security-policy gate; IAM permissions on the configured credentials remain in effect and continue to bound what the server can do.

**Impacted versions**: >= 0.2.13 AND < 1.3.47

### Patches
This issue has been addressed in awslabs.aws-api-mcp-server version 1.3.47. AWS recommends upgrading to the latest version and ensuring any forked or derivative code is patched to incorporate the new fixes.

### Workarounds
Any one of the following prevents the bypass until you can upgrade:

  - Use least-privilege IAM credentials (for example, a ReadOnlyAccess role) scoped to the task. IAM remains the primary access control and is enforced regardless of this issue.
  - If the server started during degraded connectivity, restart it once connectivity is restored so the policy enforcement data loads successfully.

### Contact
If you have any questions or comments about this advisory, AWS asks that you contact AWS Security via the [reporting page](https://aws.amazon.com/security/vulnerability-reporting) or directly via email to [aws-security@amazon.com](mailto:aws-security@amazon.com). Please do not create a public GitHub issue.

### Acknowledgement
We would like to thank Lav Kumar Vishwakarma (independent security researcher) for collaborating on this issue through the coordinated vulnerability disclosure process.

## References
- https://github.com/awslabs/mcp/security/advisories/GHSA-29w2-fq35-v728
- https://nvd.nist.gov/vuln/detail/CVE-2026-16584
- https://github.com/awslabs/mcp/pull/4315
- https://github.com/awslabs/mcp/commit/ab1bbebc097d674c1cdd4bd75a8f313be18473bf
- https://aws.amazon.com/security/security-bulletins/2026-063-aws
- https://github.com/awslabs/mcp
- https://pypi.org/project/awslabs.aws-api-mcp-server/1.3.47
