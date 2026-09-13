# [H] Roo Code Vulnerable to Potential Remote Code Execution via Model Context Protocol

## Summary
Severity: High
Advisory: CVE-2025-53098
Aliases: GHSA-5x8h-m52g-5v54
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-06-27
Source: https://osv.dev/vulnerability/CVE-2025-53098
Type: osv

## Details
Roo Code is an AI-powered autonomous coding agent. The project-specific MCP configuration for the Roo Code agent is stored in the `.roo/mcp.json` file within the VS Code workspace. Because the MCP configuration format allows for execution of arbitrary commands, prior to version 3.20.3, it would have been possible for an attacker with access to craft a prompt to ask the agent to write a malicious command to the MCP configuration file. If the user had opted-in to auto-approving file writes within the project, this would have led to arbitrary command execution. This issue is of moderate severity, since it requires the attacker to already be able to submit prompts to the agent (for instance through a prompt injection attack), for the user to have MCP enabled (on by default), and for the user to have enabled auto-approved file writes (off by default). Version 3.20.3 fixes the issue by adding an additional layer of opt-in configuration for auto-approving writing to Roo's configuration files, including all files within the `.roo/` folder.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/53xxx/CVE-2025-53098.json
- https://github.com/RooCodeInc/Roo-Code/security/advisories/GHSA-5x8h-m52g-5v54
- https://nvd.nist.gov/vuln/detail/CVE-2025-53098
- https://github.com/RooCodeInc/Roo-Code/commit/7d0b22f9e659dc6c26aab0bacbea27874986e772
