# [C] mcp-server-kubernetes argument injection can expose Kubernetes cluster credentials

## Summary
Severity: Critical
Advisory: GHSA-wmg3-h8mf-wgvr
CVE: CVE-2026-61459
CWE: CWE-88
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-07-10
Source: https://github.com/advisories/GHSA-wmg3-h8mf-wgvr
Type: github-advisory

## Affected
- PyPI: `mcp-server-kubernetes` — affected >=0 <3.9.0

## Details
MCP Server Kubernetes before 3.9.0 contains an argument injection vulnerability in structured tools (kubectl_get, kubectl_describe, kubectl_delete) that allows attackers to bypass the assertNoDangerousFlags security check by supplying resourceType and name parameters with leading dashes. Attackers can inject the --server flag to redirect kubectl commands to an attacker-controlled API server, causing the operator's bearer token to be transmitted externally and enabling full cluster compromise.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-61459
- https://github.com/Flux159/mcp-server-kubernetes/issues/328
- https://github.com/Flux159/mcp-server-kubernetes/pull/329
- https://github.com/Flux159/mcp-server-kubernetes/commit/d7890f50a4567bf5d9842541ba6f41e180227f9a
- https://github.com/Flux159/mcp-server-kubernetes
- https://github.com/Flux159/mcp-server-kubernetes/releases/tag/3.9.0
- https://www.vulncheck.com/advisories/mcp-server-kubernetes-argument-injection-via-kubectl-structured-tools
