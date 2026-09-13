# [C] n8n before 2.34.1 Remote Code Execution via Path Traversal

## Summary
Severity: Critical
Advisory: CVE-2026-77068
Aliases: GHSA-6h4x-896x-fw5m
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-20
Source: https://osv.dev/vulnerability/CVE-2026-77068
Type: osv

## Details
n8n before 2.33.4 and 2.34.x before 2.34.1 contain a remote code execution vulnerability in the @n8n/workflow-sdk node-schema loader used for MCP node-schema loading. The loader derives a node's schema module path directly from the attacker-supplied node type string without validating path-traversal sequences. An authenticated user with global:member privileges can reference malicious files via path traversal, causing code execution in the n8n main process.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/77xxx/CVE-2026-77068.json
- https://github.com/n8n-io/n8n/security/advisories/GHSA-6h4x-896x-fw5m
- https://nvd.nist.gov/vuln/detail/CVE-2026-77068
- https://www.vulncheck.com/advisories/n8n-before-remote-code-execution-via-path-traversal
