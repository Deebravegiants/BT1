# [C] Flowise OS command remote code execution

## Summary
Severity: Critical
Advisory: GHSA-2vv2-3x8x-4gv7
CVE: CVE-2025-8943
CWE: CWE-306, CWE-78
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2025-08-14
Source: https://github.com/advisories/GHSA-2vv2-3x8x-4gv7
Type: github-advisory

## Affected
- npm: `flowise` — affected >=0

## Details
The Custom MCPs feature is designed to execute OS commands, for instance, using tools like `npx` to spin up local MCP Servers. However, Flowise's inherent authentication and authorization model is minimal and lacks role-based access controls (RBAC). Furthermore, in Flowise versions before 3.0.1 the default installation operates without authentication unless explicitly configured. This combination allows unauthenticated network attackers to execute unsandboxed OS commands.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-8943
- https://github.com/FlowiseAI/Flowise
- https://research.jfrog.com/vulnerabilities/flowise-os-command-remote-code-execution-jfsa-2025-001380578
