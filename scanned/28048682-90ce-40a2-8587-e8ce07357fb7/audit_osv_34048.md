# [C] Cherry Studio is Vulnerable to OS Command Injection during Connection with a Malicious MCP Server

## Summary
Severity: Critical
Advisory: CVE-2025-54074
Aliases: GHSA-8xr5-732g-84px
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:P/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2025-08-13
Source: https://osv.dev/vulnerability/CVE-2025-54074
Type: osv

## Details
Cherry Studio is a desktop client that supports for multiple LLM providers. From versions 1.2.5 to 1.5.1, Cherry Studio is vulnerable to OS Command Injection during a connection with a malicious MCP server in HTTP Streamable mode. Attackers can setup a malicious MCP server with compatible OAuth authorization server endpoints and trick victims into connecting it, leading to OS command injection in vulnerable clients. This issue has been patched in version 1.5.2.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/54xxx/CVE-2025-54074.json
- https://github.com/CherryHQ/cherry-studio/security/advisories/GHSA-8xr5-732g-84px
- https://nvd.nist.gov/vuln/detail/CVE-2025-54074
- https://github.com/CherryHQ/cherry-studio/commit/40f9601379150854826ff3572ef7372fb0acdc38
