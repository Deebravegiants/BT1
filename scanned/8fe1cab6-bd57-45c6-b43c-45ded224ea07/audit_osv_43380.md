# [C] Flowise before 3.1.3 Remote Code Execution via Custom MCP

## Summary
Severity: Critical
Advisory: CVE-2026-73601
Aliases: GHSA-g98q-rm45-q9h8
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H)
Published: 2026-08-13
Source: https://osv.dev/vulnerability/CVE-2026-73601
Type: osv

## Details
Flowise versions before 3.1.3 contain a remote code execution vulnerability in the Custom MCP node when CUSTOM_MCP_PROTOCOL is set to stdio, allowing authenticated users to execute arbitrary commands by manipulating environment variables and command arguments. Attackers can abuse PYTHONWARNINGS and BROWSER environment variables with python3, or leverage the root working directory with node to bypass validation and execute system commands.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/73xxx/CVE-2026-73601.json
- https://github.com/FlowiseAI/Flowise/security/advisories/GHSA-g98q-rm45-q9h8
- https://nvd.nist.gov/vuln/detail/CVE-2026-73601
- https://www.vulncheck.com/advisories/flowise-before-remote-code-execution-via-custom-mcp
