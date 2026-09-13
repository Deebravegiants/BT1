# [C] MCP Toolbox for Databases vulnerable to DNS rebinding attacks

## Summary
Severity: Critical
Advisory: GHSA-7pf3-8xx7-rvhf
CVE: CVE-2026-9739
CWE: CWE-942
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:A/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H (CVSS_V4)
Published: 2026-05-28
Source: https://github.com/advisories/GHSA-7pf3-8xx7-rvhf
Type: github-advisory

## Affected
- Go: `github.com/googleapis/mcp-toolbox` — affected >=0 <1.2.0

## Details
Vulnerable to DNS rebinding attacks when using SSE (http://b/499408790). During the beta phase, we implemented `allowed-origins` and `allowed-hosts` flags to align with MCP security guidelines. However, the hardcoded `Access-Control-Allow-Origin: *` header in the SSE initialization handler was inadvertently retained. This vulnerability specifically impacts users connecting via Toolbox using SSE under specification v2024-11-05.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-9739
- https://github.com/googleapis/mcp-toolbox/issues/3053
- https://github.com/googleapis/mcp-toolbox/pull/3054
- https://github.com/googleapis/mcp-toolbox/commit/c4c7bd917e686de68e2be866cfe3872c3439efae
- https://github.com/googleapis/mcp-toolbox
