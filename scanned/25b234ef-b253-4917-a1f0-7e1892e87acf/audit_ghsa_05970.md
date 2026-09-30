# [M] utcp-gql SSRF: CVE-2026-44661 fix not applied to the GraphQL and WebSocket plugins

## Summary
Severity: Medium
Advisory: GHSA-ppx3-28rw-8fpf
CVE: CVE-2026-12210
CWE: CWE-918
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-08-25
Source: https://github.com/advisories/GHSA-ppx3-28rw-8fpf
Type: github-advisory

## Affected
- PyPI: `utcp-gql` — affected >=0 <1.1.1
- PyPI: `utcp-websocket` — affected >=0 <1.1.1

## Details
### Summary

The fix for CVE-2026-44661 (commit `5b16e43`) added the `ensure_secure_url()` / `is_secure_url()` helpers and wired them into the three HTTP-family plugins, but it did not reach the GraphQL or WebSocket plugins. The GraphQL plugin (`utcp-gql`) still uses the `startswith` prefix check that the fix explicitly replaced, so `http://127.0.0.1.attacker.example` and `http://localhost.evil.com` pass it. The WebSocket plugin (`utcp-websocket`) performs no URL validation at all, even though its own docstrings state it enforces "WSS or localhost only." Both plugins reach the same SSRF that CVE-2026-44661 was filed for, and because both attach the call template's configured auth headers to the outbound connection, the SSRF can also leak API keys and OAuth tokens to an attacker-controlled host.

### Details

In the CVE-2026-44661 fix (commit `5b16e43` ("fix(http): block SSRF via attacker-controlled OpenAPI servers[0].url")), two things in it pointed at sibling issues. The commit message says the change is "replacing the duplicated prefix check", and the new `utcp_http/_security.py` docstring names the exact bug:

> URLs whose hostname *starts* with `localhost` / `127.0.0.1` but isn't actually loopback (e.g. `http://localhost.evil.com`, `http://127.0.0.1.attacker.example`). The earlier `startswith` check let these through.

The word "duplicated" says the vulnerable check existed in more than one place. The fix only updated the three HTTP-family plugins (`http`, `streamable_http`, `sse`). The other communication-protocol plugins were also inspected.

**GraphQL plugin (`utcp-gql`).** `plugins/communication_protocols/gql/src/utcp_gql/gql_communication_protocol.py` still has the pre-fix check at line 43:

```python
def _enforce_https_or_localhost(self, url: str) -> None:
    if not (
        url.startswith("https://")
        or url.startswith("http://localhost")
        or url.startswith("http://127.0.0.1")
    ):
        raise ValueError("Security error: URL must use HTTPS or start with ...")
```

It is called on `manual_call_template.url` in `register_manual` (line 102) and on `tool_call_template.url` in `call_tool` (line 181). The URL then goes into `AIOHTTPTransport(url=...)` and a live GraphQL request.

`"http://127.0.0.1.attacker.example/graphql".startswith("http://127.0.0.1")` is `True`, so the check passes. If the attacker controls DNS for `attacker.example`, that hostname resolves to any address they choose, including `169.254.169.254`, `127.0.0.1`, or an internal `192.168.x.x` host, and the GraphQL client sends a plain-HTTP request there. `http://localhost.evil.com/graphql` behaves the same way. This is the exact prefix bypass CVE-2026-44661 was filed for.

**WebSocket plugin (`utcp-websocket`).** `plugins/communication_protocols/websocket/src/utcp_websocket/websocket_communication_protocol.py`. The module and class docstrings state:

> "Security enforcement (WSS or localhost only)"
> "Enforces security by requiring WSS or localhost connections"
> "Security validation of connection URLs"

There is no such validation in the code. `_get_connection()`, the only connection path (used by `register_manual`, `call_tool`, and `call_tool_streaming`), calls:

```python
ws = await session.ws_connect(call_template.url, headers=headers, ...)   # line 197
```

with no scheme or host check. Any URL in a `WebSocketCallTemplate` connects, including `ws://169.254.169.254/`, `ws://127.0.0.1:<internal-port>/`, or any internal hostname.

**Credential exposure.** Both plugins build connection headers in `_prepare_headers()`, which attaches the configured auth: `ApiKeyAuth` as a header, `BasicAuth` as an `Authorization: Basic` header, and `OAuth2Auth` as an `Authorization: Bearer` token. When the bypass is used to force a plain-HTTP or plain-WS connection to an attacker-resolved host, those credentials are sent to the attacker.

This is the threat model CVE-2026-44661 already established: a UTCP client ingests tool manuals, and a malicious manual is attacker-influenced. The GraphQL and WebSocket plugins consume the same kind of call template, with the same `url` field, at the same trust level as the HTTP plugins that were fixed.

Affected packages: `utcp-gql` and `utcp-websocket`, both at the current release `1.1.0`. Neither plugin has been modified since 2025-11-30, so both are unpatched on `main`.

### PoC

The discrepancy is directly observable. With `utcp-gql` and `utcp-http` installed:

```python
from utcp_gql.gql_communication_protocol import GraphQLCommunicationProtocol
from utcp_http._security import is_secure_url

bypass = "http://127.0.0.1.attacker.example/graphql"

# The fixed HTTP plugin rejects the bypass URL:
print("utcp_http is_secure_url:", is_secure_url(bypass))   # -> False

# The GraphQL plugin accepts it (no exception is raised):
GraphQLCommunicationProtocol()._enforce_https_or_localhost(bypass)
print("utcp_gql  _enforce_https_or_localhost: ACCEPTED")
```

End to end: a UTCP client that registers a manual declaring a GraphQL tool with `url: "http://127.0.0.1.<attacker-domain>/graphql"`, where that domain resolves to an internal target, issues the request to that internal service. For WebSocket, a manual declaring a tool with `url: "ws://169.254.169.254/"` connects with no check at all. To confirm the request lands, point the URL at a listener you control on a host the client can reach but the attacker cannot, or at the client's own loopback.

### Impact

Server-Side Request Forgery (CWE-918), the same class and trust boundary as CVE-2026-44661. An attacker who can get a UTCP client to register a malicious manual can:

- Make the client send GraphQL requests (GraphQL plugin) or open WebSocket connections (WebSocket plugin) to internal services and cloud metadata endpoints it would not otherwise reach.
- Force plain-HTTP / plain-WS connections to an attacker-resolved host, defeating the "HTTPS or loopback only" guarantee both plugins are meant to provide.
- Receive the call template's configured credentials (API key, Basic auth, OAuth Bearer token), because those headers are attached to the forged request.

Suggested fix. The correct helper already exists in the codebase. Promote `is_secure_url` / `ensure_secure_url` from `utcp_http` into a shared module (or replicate the `urlparse`-based hostname logic), then replace `_enforce_https_or_localhost` in the GraphQL plugin with it, and add an equivalent check in the WebSocket plugin's `_get_connection` before `ws_connect`, adapted for the `ws` and `wss` schemes. This is the same centralization commit `5b16e43` already applied to the three HTTP plugins; it just needs to cover the remaining two transports.

## Patched

- `utcp-gql` 1.1.1 replaces the broken `_enforce_https_or_localhost`
  prefix check with hostname-based `ensure_secure_url`, applied at
  both `register_manual` and `call_tool`. The underlying aiohttp
  session is also patched after `connect()` to refuse 3xx responses,
  closing the post-validation redirect SSRF on the GraphQL endpoint.
- `utcp-websocket` 1.1.1 introduces `ensure_secure_ws_url` (the
  WebSocket-scheme companion of `ensure_secure_url`) and enforces it
  in both the `WebSocketCallTemplate` Pydantic field validator and
  `_get_connection`. `ws_connect` is called with `allow_redirects=False`.
  The OAuth2 token-fetch path uses the same redirect-safe helper
  introduced in `utcp-http` 1.1.4.

Both plugins duplicate `_security.py` from `utcp-http` (rather than
adding a cross-plugin runtime dependency); keep the copies in sync
when changing validator behaviour.

Upgrade to `utcp-gql >= 1.1.1` and/or `utcp-websocket >= 1.1.1`. No
workaround in earlier versions.

## References
- https://github.com/universal-tool-calling-protocol/python-utcp/security/advisories/GHSA-ppx3-28rw-8fpf
- https://nvd.nist.gov/vuln/detail/CVE-2026-12210
- https://github.com/gola-leya/cve_submit/issues/1
- https://github.com/universal-tool-calling-protocol/python-utcp/issues/86
- https://github.com/universal-tool-calling-protocol/python-utcp/commit/fc3268e2a62e1181f91a63faf0a9bcee7639db29
- https://github.com/universal-tool-calling-protocol/python-utcp
- https://vuldb.com/cve/CVE-2026-12210
- https://vuldb.com/submit/832542
- https://vuldb.com/vuln/370852
