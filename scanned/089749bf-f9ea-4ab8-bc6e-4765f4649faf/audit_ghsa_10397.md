# [C] aws-mcp has a Command Injection Remote Code Execution Vulnerability

## Summary
Severity: Critical
Advisory: GHSA-fgmx-xfp3-w28p
CVE: CVE-2026-5059
CWE: CWE-78
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-04-11
Source: https://github.com/advisories/GHSA-fgmx-xfp3-w28p
Type: github-advisory

## Affected
- PyPI: `aws-mcp` — affected >=0

## Details
aws-mcp-server AWS CLI Command Injection Remote Code Execution Vulnerability. This vulnerability allows remote attackers to execute arbitrary code on affected installations of aws-mcp-server. Authentication is not required to exploit this vulnerability.

The specific flaw exists within the handling of the allowed commands list. The issue results from the lack of proper validation of a user-supplied string before using it to execute a system call. An attacker can leverage this vulnerability to execute code in the context of the MCP server. Was ZDI-CAN-27969.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-5059
- https://github.com/alexei-led/aws-mcp-server
- https://www.zerodayinitiative.com/advisories/ZDI-26-245
