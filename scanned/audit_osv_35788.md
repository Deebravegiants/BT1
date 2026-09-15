# [C] Authorization Bypass in MCP Toolbox Legacy HTTP Endpoints

## Summary
Severity: Critical
Advisory: CVE-2026-14537
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:U)
Published: 2026-07-31
Source: https://osv.dev/vulnerability/CVE-2026-14537
Type: osv

## Details
Incorrect Authorization in the direct HTTP API tool invocation endpoint in Google mcp-toolbox versions v1.3.0 and v1.4.0 allows an unauthenticated attacker to invoke tools protected by the scopeRequired feature via sending tool invocation requests through legacy HTTP endpoints when the --enable-api flag is active.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/14xxx/CVE-2026-14537.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-14537
- https://github.com/googleapis/mcp-toolbox/pull/3435
