# [H] MCP Inspector is Vulnerable to Potential Command Execution via XSS When Connecting to an Untrusted MCP Server

## Summary
Severity: High
Advisory: GHSA-g9hg-qhmf-q45m
CVE: CVE-2025-58444
CWE: CWE-79, CWE-84, CWE-94
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:A/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-09-08
Source: https://github.com/advisories/GHSA-g9hg-qhmf-q45m
Type: github-advisory

## Affected
- npm: `@modelcontextprotocol/inspector` — affected >=0 <0.16.6

## Details
An XSS flaw exists in the MCP Inspector local development tool when it renders a redirect URL returned by a remote MCP server. If the Inspector connects to an untrusted server, a crafted redirect can inject script into the Inspector context and, via the built-in proxy, be leveraged to trigger arbitrary command execution on the developer machine. Version 0.16.6 hardens URL handling/validation and prevents script execution.

> Thank you to the following researchers for their reports and contributions:
> * Raymond (Veria Labs)
> * Gavin Zhong, <superboyzjc@gmail.com> & Shuyang Wang, <swang@obsidiansecurity.com>.

## References
- https://github.com/modelcontextprotocol/inspector/security/advisories/GHSA-g9hg-qhmf-q45m
- https://nvd.nist.gov/vuln/detail/CVE-2025-58444
- https://github.com/modelcontextprotocol/inspector/commit/650f3090d26344a672026b737d81586595bb1f60
- https://github.com/modelcontextprotocol/inspector
- https://www.npmjs.com/package/@modelcontextprotocol/inspector/v/0.16.6
