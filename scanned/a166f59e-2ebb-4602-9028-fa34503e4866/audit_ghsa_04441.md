# [C] npm PraisonAI MCPServer exposes unauthenticated HTTP tools/call

## Summary
Severity: Critical
Advisory: GHSA-j4f3-55x4-r6q2
CVE: CVE-2026-57139
CWE: CWE-1188, CWE-306, CWE-862
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-06-18
Source: https://github.com/advisories/GHSA-j4f3-55x4-r6q2
Type: github-advisory

## Affected
- npm: `praisonai` — affected >=1.5.0 <1.7.2

## Details
## Summary

The published npm package `praisonai` exports a TypeScript `MCPServer` that can expose tools, resources, and prompts over an HTTP JSON-RPC transport with:

```ts
await server.start({ port: 3000 });
```

The HTTP transport has no authentication or authorization path. `MCPServerConfig` does not expose an auth/security setting, `startHttp()` ignores the `Authorization` header, and every POST request is parsed and forwarded directly to `handleRequest()`. That request handler dispatches sensitive MCP methods such as `tools/call`, `resources/read`, and `prompts/get`.

The implementation also calls `this.httpServer.listen(port)` without a host argument. In Node.js this binds to the unspecified address; the local PoV observed `{ address: "::", family: "IPv6" }`, making the service reachable on all interfaces on systems where the port is exposed.

This lets any network client that can reach the HTTP port list tools and invoke registered server-side tools without credentials. Supplying `Authorization: Bearer invalid` makes no difference.

## Technical Details

`MCPServerConfig` exposes server metadata, tools/resources/prompts, stdio, port, and logging. It does not expose an auth token, authorization policy, `MCPSecurity` instance, authorization callback, or loopback-only option:

```text
src/praisonai-ts/src/mcp/server.ts
  57: export interface MCPServerConfig {
  63:     tools?: MCPServerTool[];
  65:     resources?: MCPResource[];
  67:     prompts?: MCPPrompt[];
  69:     stdio?: boolean;
  73:     port?: number | null;
  75:     logging?: boolean;
```

`handleRequest()` dispatches sensitive MCP methods directly:

```text
src/praisonai-ts/src/mcp/server.ts
  203: async handleRequest(request: MCPRequest): Promise<MCPResponse> {
  219:     case 'tools/call':
  220:       result = await this.handleToolCall(params);
  225:     case 'resources/read':
  226:       result = await this.handleResourceRead(params);
  231:     case 'prompts/get':
  232:       result = await this.handlePromptGet(params);
```

The tool dispatcher invokes the registered handler:

```text
src/praisonai-ts/src/mcp/server.ts
  285: private async handleToolCall(params?: any): Promise<any> {
  288:   const tool = this.tools.get(name);
  298:   const result = await tool.handler(args ?? {});
```

The HTTP server parses every POST body and forwards it to `handleRequest()` with no authentication check:

```text
src/praisonai-ts/src/mcp/server.ts
  403: async startHttp(port: number): Promise<void> {
  409:   this.httpServer = http.createServer(async (req, res) => {
  416:     const response = await this.handleRequest(request);
  434:   this.httpServer.listen(port, () => {
```

This is a guard-coverage gap because the same TypeScript package already ships a dedicated MCP security manager:

```text
src/praisonai-ts/src/mcp/security.ts
  2:  * MCP Security - Authentication, authorization, and rate limiting
  79: export class MCPSecurity {
  132: async check(request: { path?: string; method?: string; headers?: ... })
  167: const auth = headers['authorization'] ?? headers['Authorization'];
  239: case 'authenticate':
  303: export function createApiKeyPolicy(...)
```

`MCPServer` never references that security manager in its HTTP request path.

### Why This Is Not Intended Behavior

PraisonAI's MCP documentation says MCP servers allow AI models to use tools and communicate with external systems. The same page's security considerations say to use API keys in production, implement rate limiting, validate incoming requests, use HTTPS, and limit custom tool permissions.

PraisonAI's security page also documents prior breaking hardening where API servers were changed to require authentication by default and bind to `127.0.0.1` instead of `0.0.0.0`. It separately lists MCP `tools/call` issues as security vulnerabilities.

The npm TypeScript `MCPServer` does the opposite:

- `start({ port })` binds to the unspecified address;
- `MCPServerConfig` has no auth/security field;
- `startHttp()` does not inspect `Authorization`;
- `tools/list`, `tools/call`, `resources/read`, and `prompts/get` all dispatch without authentication; and
- `MCPSecurity` exists but is not wired into the HTTP server.

This is not merely a deployment hardening suggestion. The package exposes an HTTP MCP server API and a separate security manager, but the server's own HTTP transport provides no way to enforce the documented API-key requirement.

## PoV

The PoV installs the published npm package in a temporary project, starts the exported `MCPServer` on a local ephemeral port, and sends loopback JSON-RPC requests. It does not call any LLM provider or external service after package installation.

Run from a local reproduction checkout:

```fish
node poc/pov_poc.js 1.7.1
```

Observed result:

```json
{
  "package": "praisonai",
  "version": "1.7.1",
  "mcpServerExported": true,
  "bindAddress": {
    "address": "::",
    "family": "IPv6"
  },
  "initialize": {
    "status": 200
  },
  "list": {
    "status": 200,
    "json": {
      "result": {
        "tools": [
          {
            "name": "admin_reset_marker",
            "description": "privileged marker tool"
          }
        ]
      }
    }
  },
  "callNoAuth": {
    "status": 200,
    "json": {
      "result": {
        "content": [
          {
            "text": "invoked:NO_AUTH_MARKER"
          }
        ]
      }
    }
  },
  "callBadAuth": {
    "status": 200,
    "json": {
      "result": {
        "content": [
          {
            "text": "invoked:BAD_AUTH_MARKER"
          }
        ]
      }
    }
  },
  "calls": [
    "NO_AUTH_MARKER",
    "BAD_AUTH_MARKER"
  ],
  "patchedControl": {
    "noAuthStatus": 401,
    "withAuthStatus": 200,
    "patchedCalls": [
      "called"
    ]
  }
}
```

Interpretation:

- unauthenticated `initialize` returns `200`;
- unauthenticated `tools/list` returns the registered tool;
- unauthenticated `tools/call` invokes the registered tool;
- invalid `Authorization: Bearer invalid` is ignored and also invokes the tool;
- the server binds to the unspecified IPv6 address; and
- a minimal local wrapper that enforces a bearer token blocks the same no-auth call with `401`, demonstrating that the PoV is exercising the missing authentication boundary.

## PoC

The PoV section above contains the local reproduction command, input, and decisive output.

## Impact

Any client that can reach the npm TypeScript `MCPServer` HTTP port can list and invoke all registered MCP tools without credentials.

Real impact depends on which tools, resources, and prompts the application registers. MCP tools commonly wrap filesystem operations, API clients, database queries, agent actions, deployment operations, email/Slack actions, browser automation, and code execution. Because those handlers run with the server process privileges and server-side credentials, an unauthenticated caller can drive the same actions.

`resources/read` and `prompts/get` are also unauthenticated and may disclose application data or prompt material registered by the server.

### Severity

Suggested severity: Critical.

Rationale:

- `AV`: exploitation is a direct HTTP JSON-RPC request.
- `AC`: no race, user gesture, or special state is required.
- `PR`: no credentials are required; invalid credentials are ignored.
- `UI`: no user interaction is required after the server is running.
- `S`: impact is within the authority of the MCP server process and its registered tools.
- `C`: resources, prompts, and tool-returned data may expose sensitive data.
- `I`: unauthenticated callers can drive server-side tools.
- `A`: unauthenticated callers can invoke destructive or resource-consuming tools if registered.

## Suggested Fix

Recommended minimum fix:

1. Add `security`, `auth`, `authRequired`, `apiKeys`, or `authorize(req)` to `MCPServerConfig`.
2. Fail closed for HTTP transport when auth is not configured, unless the caller explicitly opts into unauthenticated loopback-only development mode.
3. Bind HTTP transport to `127.0.0.1` by default, or require an explicit host when binding to all interfaces.
4. Call `MCPSecurity.check(...)` or equivalent middleware before every non-health POST request reaches `handleRequest()`.
5. Return `401` for missing or invalid credentials before dispatching `initialize`, `tools/list`, `tools/call`, `resources/read`, or `prompts/get`.
6. Add Origin/Host protections for loopback HTTP transports to reduce DNS rebinding exposure.
7. Add regression tests proving:
   - no-auth `tools/list` returns `401`;
   - no-auth `tools/call` returns `401` and does not invoke the handler;
   - invalid bearer token returns `401`;
   - valid bearer token invokes the handler;
   - default `start({ port })` does not bind to all interfaces without an explicit opt-in.

## Affected Package/Versions

- Repository: `MervinPraison/PraisonAI`
- Ecosystem: `npm`
- Package: `praisonai`
- Component: `src/praisonai-ts/src/mcp/server.ts`
- Related unused security component: `src/praisonai-ts/src/mcp/security.ts`
- Current npm version checked: `1.7.1`
- Refreshed `origin/main` checked: `1ad58ca02975ff1398efeda694ea2ab78f20cf3e`

Confirmed affected range:

```text
>= 1.5.0, <= 1.7.1
```

Boundary:

```text
1.4.0 does not export MCPServer and does not ship dist/mcp/server.js.
```

No fixed npm version is known at the time of this report.

### Version Sweep

The included sweep installs selected npm versions and checks the HTTP `MCPServer` path:

```fish
node poc/version_sweep_poc.js
```

Observed result:

```text
1.4.0: mcpServerExported=false, hasDistMcpServer=false
1.5.0: mcpServerExported=true, hasDistMcpServer=true, noAuthToolCallInvoked=true, bindAddress=::
1.5.4: mcpServerExported=true, hasDistMcpServer=true, noAuthToolCallInvoked=true, bindAddress=::
1.6.0: mcpServerExported=true, hasDistMcpServer=true, noAuthToolCallInvoked=true, bindAddress=::
1.7.0: mcpServerExported=true, hasDistMcpServer=true, noAuthToolCallInvoked=true, bindAddress=::
1.7.1: mcpServerExported=true, hasDistMcpServer=true, noAuthToolCallInvoked=true, bindAddress=::
```

## Advisory History

Known related public advisories:

- `GHSA-9mqq-jqxf-grvw` / `CVE-2026-44336`: `pip:praisonai` MCP `tools/call` path traversal to RCE in Python `praisonai mcp serve`, affected `<= 4.6.33`.
- `CVE-2026-47394`: `pip:praisonai` incomplete MCP path traversal fix affecting Python workflow/deploy handlers.
- poc: deprecated Python MCP SSE Host/Origin/session issue.
- poc: npm TypeScript AgentOS missing authentication.

This report is distinct because it targets:

- ecosystem: `npm`;
- package: `praisonai`;
- component: `src/praisonai-ts/src/mcp/server.ts`;
- root cause: TypeScript `MCPServer` HTTP transport missing auth and not using `MCPSecurity`;
- primitive: unauthenticated and invalid-auth JSON-RPC `tools/call` invokes arbitrary registered TypeScript MCP tools; and
- affected range: `>= 1.5.0, <= 1.7.1`.

The Python MCP advisories cover path traversal in specific Python MCP tool handlers. They do not cover the npm TypeScript `MCPServer` transport or its unwired security manager.

## References
- https://github.com/MervinPraison/PraisonAI/security/advisories/GHSA-j4f3-55x4-r6q2
- https://github.com/MervinPraison/PraisonAI
