# [C] REC in MCPJam inspector due to HTTP Endpoint exposes

## Summary
Severity: Critical
Advisory: GHSA-232v-j27c-5pp6
CVE: CVE-2026-23744
CWE: CWE-306
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-01-16
Source: https://github.com/advisories/GHSA-232v-j27c-5pp6
Type: github-advisory

## Affected
- npm: `@mcpjam/inspector` — affected >=0 <1.4.3

## Details
### Summary
MCPJam inspector is the local-first development platform for MCP servers. The Latest version Versions 1.4.2 and earlier are vulnerable to remote code execution (RCE) vulnerability, which allows an attacker to send a crafted HTTP request that triggers the installation of an MCP server, leading to RCE.

This vulnerability is similar to CVE-2025-49596, but more severe. While CVE-2025-49596 requires tricking a user into clicking a malicious link, this vulnerability is exploitable with no user interaction. Since MCPJam inspector by default listens on 0.0.0.0 instead of 127.0.0.1, an attacker can trigger the RCE remotely via a simple HTTP request.



### Details
MCPJam inspector binds to `0.0.0.0` making its HTTP APIs remotely reachable.
``` TypeScript
const server = serve({
  fetch: app.fetch,
  port: SERVER_PORT,
  hostname: "0.0.0.0",
});
```

The `/api/mcp/connect` API, which is intended for connecting to MCP servers, becomes an open entry point for unauthorized requests. When an HTTP request reaches the `/connect` route, the system extracts the `command` and `args` fields without performing any security checks, leading to the execution of arbitrary command.

### PoC
(1) Start up the MCPJam inspector as Github README
`npx @mcpjam/inspector@latest`

(2) RCE by posting a HTTP request
A remote code execution (RCE) attack can be triggered by sending a simple HTTP request to the target host running MCPJam inspector (e.g., http://10.97.58.83:6274 in the test environment).
`curl http://10.97.58.83:6274/api/mcp/connect --header "Content-Type: application/json" --data "{\"serverConfig\":{\"command\":\"cmd.exe\",\"args\":[\"/c\", \"calc\"],\"env\":{}},\"serverId\":\"mytest\"}"`


<img width="1669" height="1397" alt="image" src="https://github.com/user-attachments/assets/cb6505f1-3cdd-4c64-8f39-a01619a63411" />


### Impact
Remote Code Execution (RCE)

## References
- https://github.com/MCPJam/inspector/security/advisories/GHSA-232v-j27c-5pp6
- https://nvd.nist.gov/vuln/detail/CVE-2026-23744
- https://github.com/MCPJam/inspector/commit/e6b9cf9d9e6c9cbec31493b1bdca3a1255fe3e7a
- https://github.com/MCPJam/inspector
