# [C] Flowise: Authenticated RCE Via MCP Adapters

## Summary
Severity: Critical
Advisory: GHSA-c9gw-hvqq-f33r
CVE: CVE-2026-40933
CWE: CWE-78
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-04-16
Source: https://github.com/advisories/GHSA-c9gw-hvqq-f33r
Type: github-advisory

## Affected
- npm: `flowise` — affected >=0 <3.1.0
- npm: `flowise-components` — affected >=0 <3.1.0

## Details
### Summary
Due to unsafe serialization of stdio commands in the MCP adapter, an authenticated attacker can add an MCP stdio server with an arbitrary command, achieving command execution.

### Details
The vulnerability lies in a bug in the input sanitization from the “Custom MCP” configuration in http://localhost:3000/canvas - where any user can add a new MCP, when doing so - adding a new MCP using stdio, the user can add any command, even though your code have input sanitization checks such as validateCommandInjection and validateArgsForLocalFileAccess, and a list of predefined specific safe commands - these commands, for example "npx" can be combined with code execution arguments ("-c touch /tmp/pwn") that enable direct code execution on the underlying OS.

https://github.com/FlowiseAI/Flowise/blob/d848baeb6bd9737a1e7fc912349c45fbdcc7bb38/packages/components/nodes/tools/MCP/core.ts#L223

https://github.com/FlowiseAI/Flowise/blob/d848baeb6bd9737a1e7fc912349c45fbdcc7bb38/packages/components/nodes/tools/MCP/core.ts#L177

https://github.com/FlowiseAI/Flowise/blob/d848baeb6bd9737a1e7fc912349c45fbdcc7bb38/packages/components/nodes/tools/MCP/core.ts#L269


### PoC
Create a new Custom MCP and add an "npx -c" command.
```
{
    "command": "npx",
    "args": [
        "-c",
        "touch /tmp/pwn"
    ]
}
```
<img width="358" height="628" alt="Screenshot 2026-01-12 at 18 32 37" src="https://github.com/user-attachments/assets/d95c1ae2-23a7-4afe-b586-722003baf50e" />

### Impact
This is an authenticated arbitrary command execution due to unsanitized input, even though the input is sanitized, more protections should be added in order to close ways for attackers to execute arbitrary commands.

## References
- https://github.com/FlowiseAI/Flowise/security/advisories/GHSA-c9gw-hvqq-f33r
- https://github.com/FlowiseAI/Flowise
- https://www.ox.security/blog/mcp-supply-chain-advisory-rce-vulnerabilities-across-the-ai-ecosystem
- https://www.ox.security/blog/the-mother-of-all-ai-supply-chains-critical-systemic-vulnerability-at-the-core-of-the-mcp
