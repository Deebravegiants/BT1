# [C] Flowise has Remote Code Execution vulnerability

## Summary
Severity: Critical
Advisory: CVE-2025-59528
Aliases: GHSA-3gcm-f6qx-ff7p
CVSS: 10.0 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H)
Published: 2025-09-22
Source: https://osv.dev/vulnerability/CVE-2025-59528
Type: osv

## Details
Flowise is a drag & drop user interface to build a customized large language model flow. In version 3.0.5, Flowise is vulnerable to remote code execution. The CustomMCP node allows users to input configuration settings for connecting to an external MCP server. This node parses the user-provided mcpServerConfig string to build the MCP server configuration. However, during this process, it executes JavaScript code without any security validation. Specifically, inside the convertToValidJSONString function, user input is directly passed to the Function() constructor, which evaluates and executes the input as JavaScript code. Since this runs with full Node.js runtime privileges, it can access dangerous modules such as child_process and fs. This issue has been patched in version 3.0.6.

## References
- https://github.com/FlowiseAI/Flowise/blob/5930f1119c655bcf8d2200ae827a1f5b9fec81d0/packages/components/nodes/tools/MCP/CustomMCP/CustomMCP.ts#L132
- https://github.com/FlowiseAI/Flowise/blob/5930f1119c655bcf8d2200ae827a1f5b9fec81d0/packages/components/nodes/tools/MCP/CustomMCP/CustomMCP.ts#L220
- https://github.com/FlowiseAI/Flowise/blob/5930f1119c655bcf8d2200ae827a1f5b9fec81d0/packages/components/nodes/tools/MCP/CustomMCP/CustomMCP.ts#L262-L270
- https://github.com/FlowiseAI/Flowise/blob/5930f1119c655bcf8d2200ae827a1f5b9fec81d0/packages/server/src/controllers/nodes/index.ts#L57-L78
- https://github.com/FlowiseAI/Flowise/blob/5930f1119c655bcf8d2200ae827a1f5b9fec81d0/packages/server/src/routes/node-load-methods/index.ts#L5
- https://github.com/FlowiseAI/Flowise/blob/5930f1119c655bcf8d2200ae827a1f5b9fec81d0/packages/server/src/services/nodes/index.ts#L91-L94
- https://github.com/FlowiseAI/Flowise/releases/tag/flowise%403.0.6
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/59xxx/CVE-2025-59528.json
- https://github.com/FlowiseAI/Flowise/security/advisories/GHSA-3gcm-f6qx-ff7p
- https://nvd.nist.gov/vuln/detail/CVE-2025-59528
