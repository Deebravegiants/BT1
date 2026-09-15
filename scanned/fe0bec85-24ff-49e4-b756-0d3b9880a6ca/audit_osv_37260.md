# [H] CVE-2026-30624

## Summary
Severity: High
Advisory: CVE-2026-30624
CVSS: 8.6 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:H)
Published: 2026-04-15
Source: https://osv.dev/vulnerability/CVE-2026-30624
Type: osv

## Details
Agent Zero 0.9.8 contains a remote code execution vulnerability in its External MCP Servers configuration feature. The application allows users to define MCP servers using a JSON configuration containing arbitrary command and args values. These values are executed by the application when the configuration is applied without sufficient validation or restriction. An attacker may supply a malicious MCP configuration to execute arbitrary operating system commands, potentially resulting in remote code execution with the privileges of the Agent Zero process.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/30xxx/CVE-2026-30624.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-30624
- https://www.ox.security/blog/mcp-supply-chain-advisory-rce-vulnerabilities-across-the-ai-ecosystem/
