# [H] Streamable HTTP mode exposes LINE Desktop read/send tools without MCP authentication

## Summary
Severity: High
Advisory: GHSA-4hf8-5mjm-rfgq
CVE: CVE-2026-49357
CWE: CWE-306, CWE-862
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-06-26
Source: https://github.com/advisories/GHSA-4hf8-5mjm-rfgq
Type: github-advisory

## Affected
- npm: `line-desktop-mcp` — affected >=0 <1.1.2

## Details
# Streamable HTTP mode exposes LINE Desktop read/send tools without MCP authentication

## Summary

`line-desktop-mcp` supports a `--http-mode` Streamable HTTP transport for use with clients such as n8n. In this mode the server binds to `0.0.0.0` and exposes the MCP `/mcp` endpoint without an MCP-layer authentication check. Any network client that can reach the port can initialize a session, list tools, and call tools that read LINE Desktop chat history or send LINE messages through the already logged-in desktop application.

This is High for deployments where the HTTP port is reachable beyond the local host, because the server acts with the user authority of the logged-in LINE Desktop session. It is lower if the listener is strictly firewalled to trusted local clients.

## Affected version

Repository: `dtwang/line-desktop-mcp`

Current source checked: `fbed0d2d3048e63f48a356a1267ed8ec5e78f3ae` on `main`, committed 2026-05-14.

Published npm package checked: `line-desktop-mcp@1.1.1`.

## Source evidence

`README.md` documents Streamable HTTP mode:

```text
npx line-desktop-mcp@latest --http-mode --port 3000
```

The same README documents MCP endpoints at `/mcp` and explains that this mode is intended for clients such as n8n.

`src/server.js` registers LINE Desktop tools including:

- `get_line_chatroom_history_default`
- `get_line_chatroom_history_long`
- `get_line_chatroom_history_short`
- `send_message_manual`
- `send_message_auto`

Those tool handlers call into the desktop automation layer: `getChatHistory(...)` and `sendChatMessage(...)`.

In HTTP mode, `src/server.js` creates an Express app and Streamable HTTP transport, accepts POSTs to `/mcp`, creates sessions, connects the transport to the MCP server, and calls `transport.handleRequest(...)`. I did not find an authentication or bearer-token check before session creation or tool invocation.

The listener is explicitly network-bound:

```js
app.listen(port, 0.0.0.0, () => {
  console.error(`LINE Desktop MCP Server running on Streamable HTTP mode`);
  console.error(`  Local:   http://127.0.0.1:${port}${endpoint}`);
  console.error(`  Network: http://0.0.0.0:${port}${endpoint}`);
});
```

## Vulnerability chain

1. A user starts the server with `--http-mode --port 3000`.
2. The server binds on `0.0.0.0:3000`, not only loopback.
3. A network client reaches `/mcp` and sends the normal MCP initialize request.
4. The server creates a Streamable HTTP session without authenticating the caller.
5. The caller can list and invoke LINE Desktop tools.
6. Tool calls execute through the logged-in LINE Desktop application on the user workstation.

## Impact

An unauthenticated network client can read LINE chat history through the MCP history tools and can send LINE messages through the send-message tools, including `send_message_auto` when the tool call requests immediate sending. The attacker does not need LINE credentials or a LINE API token; they only need network reachability to the MCP HTTP port.

The practical impact is disclosure of private LINE conversations and unauthorized messages sent as the logged-in desktop user.

## Suggested fix

Require authentication before accepting Streamable HTTP MCP sessions or tool calls. For example:

- require a bearer token or local secret when `--http-mode` is used;
- bind HTTP mode to `127.0.0.1` by default unless the operator explicitly opts into network exposure;
- refuse to start `0.0.0.0` HTTP mode without authentication;
- document that `host.docker.internal` / n8n setups must still authenticate to the MCP server.

A defense-in-depth improvement would also keep `send_message_auto` disabled unless explicitly enabled by a server-side flag, because it converts MCP tool access into immediate message sending as the desktop user.

## References
- https://github.com/dtwang/line-desktop-mcp/security/advisories/GHSA-4hf8-5mjm-rfgq
- https://nvd.nist.gov/vuln/detail/CVE-2026-49357
- https://github.com/dtwang/line-desktop-mcp/commit/680617894981ea93f8f6ceb51ecde7519754d501
- https://github.com/dtwang/line-desktop-mcp
