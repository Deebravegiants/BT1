# [H] CamoFox MCP: Unauthenticated HTTP MCP browser-control surface

## Summary
Severity: High
Advisory: GHSA-7hgr-7h44-33w2
CWE: CWE-306
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:L/VI:N/VA:N/SC:H/SI:H/SA:L (CVSS_V4)
Published: 2026-05-19
Source: https://github.com/advisories/GHSA-7hgr-7h44-33w2
Type: github-advisory

## Affected
- npm: `camofox-mcp` — affected >=0 <1.13.2

## Details
# Unauthenticated HTTP MCP browser-control surface in `camofox-mcp`

## Summary

`camofox-mcp` exposed a Streamable HTTP MCP endpoint at `/mcp` with rate limiting but no inbound MCP-layer authentication. When HTTP mode was enabled, any client that could reach `/mcp` could list and invoke browser-control tools.

If `CAMOFOX_API_KEY` was configured, the server then forwarded that server-side key to the underlying `camofox-browser` backend. That means an unauthenticated MCP caller could exercise the server's browser authority without knowing the backend browser API key.

Reviewed vulnerable commit: `10e3ac08cb50d830eb4ee00a789229f02f28a1a4`
Fixed commit observed on main: `599f56ee40f8062aeca541c251ed1d39fb437f50`
Fixed release observed: `v1.13.2`
Suggested severity: High, with the caveat that default loopback-only deployments reduce practical exposure.

## Root cause

In the reviewed commit, `src/http.ts` creates the Express MCP app and applies only a rate limiter to `/mcp`:

```ts
const app = createMcpExpressApp({ host: config.httpHost });

const limiter = rateLimit({
  windowMs: 60_000,
  limit: config.httpRateLimit,
  standardHeaders: true,
  legacyHeaders: false
});

app.use("/mcp", limiter);
```

The `POST /mcp` handler then creates a server and `StreamableHTTPServerTransport` and passes the request body into the MCP transport without checking `Authorization`, an inbound API key, allowed hosts, or public-bind safety:

```ts
app.post("/mcp", async (req: any, res: any) => {
  try {
    const { server } = createServer(config);
    const transport = new StreamableHTTPServerTransport({ sessionIdGenerator: undefined });

    await server.connect(transport);
    await transport.handleRequest(req, res, req.body);
```

`src/config.ts` made HTTP mode configurable and defaulted the HTTP host to loopback, but it did not require an inbound HTTP client secret:

```ts
transport: cli.transport ?? envTransport ?? "stdio",
httpPort: cli.httpPort ?? (Number.isNaN(httpPortFromEnv) ? 3000 : httpPortFromEnv),
httpHost: cli.httpHost ?? env.CAMOFOX_HTTP_HOST ?? "127.0.0.1",
```

Separately, `src/client.ts` forwarded `CAMOFOX_API_KEY` server-side to the browser backend:

```ts
if (this.apiKey) {
  headers.set("x-api-key", this.apiKey);
  headers.set("authorization", `Bearer ${this.apiKey}`);
}
```

So `CAMOFOX_API_KEY` protected the MCP server's outbound requests to the backend browser service, but did not authenticate inbound HTTP MCP clients.

## Auth boundary

The vulnerable boundary was the HTTP MCP endpoint. The client did not need to provide `Authorization` or any `CAMOFOX_API_KEY` value to call MCP tools.

The default bind was `127.0.0.1`, which lowers severity for default local-only deployments. The risky cases are documented HTTP/remote-client deployments, Docker/port-forwarded deployments, or any environment where a browser page, local network client, reverse proxy, or another user can reach the `/mcp` endpoint.

## Proof of concept

I used a fake `camofox-browser` backend so no real browser was launched and no external navigation occurred. The harness starts the reviewed `dist/http.js` server with `CAMOFOX_API_KEY=server-side-secret`, connects an MCP SDK client to `/mcp` with no auth headers, lists tools, then calls `create_tab` and `navigate`.

Observed output:

```json
{
  "authUsedByClient": false,
  "listedToolCount": 46,
  "backendRequests": [
    {
      "method": "POST",
      "url": "/tabs",
      "headers": {
        "authorization": "Bearer server-side-secret",
        "x-api-key": "server-side-secret"
      }
    },
    {
      "method": "POST",
      "url": "/tabs/fake-tab-1/navigate",
      "headers": {
        "authorization": "Bearer server-side-secret",
        "x-api-key": "server-side-secret"
      }
    }
  ],
  "observedUnauthenticatedBrowserControl": true,
  "serverSideSecretForwardedToBackend": true
}
```

This demonstrates both parts of the issue:

1. The MCP client used no inbound authentication.
2. The server still used its configured backend browser secret when forwarding the tool calls.

## Impact

An unauthenticated client that can reach the HTTP MCP endpoint can exercise browser-control tools as the MCP server. Depending on the user's active browser profiles and configured backend, that can allow page navigation, tab creation, interaction with authenticated browser contexts, screenshot/content observation, and other browser-automation actions exposed by the MCP tool surface.

The impact is strongest when HTTP mode is intentionally exposed for remote MCP clients or through Docker/reverse-proxy deployment and the operator assumes `CAMOFOX_API_KEY` protects the whole control plane.

## Fix notes

The public issue indicates this has been fixed in `599f56e` and released as `v1.13.2` by adding dedicated inbound `CAMOFOX_HTTP_API_KEY` Bearer auth, public-bind startup validation, auth before `/mcp` JSON parsing, loopback Host-header protection, and optional allowed-hosts handling. Those are the right mitigation directions.

## References
- https://github.com/redf0x1/camofox-mcp/security/advisories/GHSA-7hgr-7h44-33w2
- https://github.com/redf0x1/camofox-mcp/commit/599f56ee40f8062aeca541c251ed1d39fb437f50
- https://github.com/redf0x1/camofox-mcp
