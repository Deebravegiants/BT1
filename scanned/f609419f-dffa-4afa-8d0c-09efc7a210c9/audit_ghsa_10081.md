# [C] Upsonic: remote code execution vulnerability in its MCP server/task creation functionality

## Summary
Severity: Critical
Advisory: GHSA-cw73-5f7h-m4gv
CVE: CVE-2026-30625
CWE: CWE-77
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-04-15
Source: https://github.com/advisories/GHSA-cw73-5f7h-m4gv
Type: github-advisory

## Affected
- PyPI: `upsonic` — affected >=0 <0.72.0

## Details
Upsonic 0.71.6 contains a remote code execution vulnerability in its MCP server/task creation functionality. The application allows users to define MCP tasks with arbitrary command and args values. Although an allowlist exists, certain allowed commands (npm, npx) accept argument flags that enable execution of arbitrary OS commands. Maliciously crafted MCP tasks may lead to remote code execution with the privileges of the Upsonic process. In version 0.72.0 Upsonic added a warning about using Stdio servers being able to execute commands directly on the machine.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-30625
- https://github.com/Upsonic/Upsonic/commit/855053fce0662227d9246268ff4a0844b481a305
- https://github.com/Upsonic/Upsonic
- https://www.ox.security/blog/mcp-supply-chain-advisory-rce-vulnerabilities-across-the-ai-ecosystem
