# [C] mcp-pinot: Unauthenticated tool invocation via default oauth_enabled=False + host 0.0.0.0 bind

## Summary
Severity: Critical
Advisory: GHSA-73cv-556c-w3g6
CVE: CVE-2026-49257
CWE: CWE-306
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-06-26
Source: https://github.com/advisories/GHSA-73cv-556c-w3g6
Type: github-advisory

## Affected
- PyPI: `mcp-pinot-server` — affected >=0 <3.1.0

## Details
## Resolution

Fixed in [v3.1.0](https://github.com/startreedata/mcp-pinot/releases/tag/v3.1.0), released 2026-05-25. The fix was merged in [PR #95](https://github.com/startreedata/mcp-pinot/pull/95) at commit [`1c7d3f9`](https://github.com/startreedata/mcp-pinot/commit/1c7d3f9cd384854bf72c127d230bdb32299475ad).

The fix changes the default HTTP bind host to `127.0.0.1`, refuses non-loopback HTTP/HTTPS exposure unless OAuth is enabled, makes Helm exposure opt-in and OAuth-gated, and adds parser-backed single-statement read-only validation for `read-query`.

## CVSS evaluation

Reviewed on 2026-05-25. The advisory remains **Critical** with `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H` = **10.0**.

Rationale:

| Metric | Value | Reason |
|---|---|---|
| AV | Network | The default HTTP server bound to `0.0.0.0:8080` and accepted remote HTTP requests. |
| AC | Low | Exploitation required only a direct MCP tool call. |
| PR | None | OAuth was disabled by default. |
| UI | None | No user interaction was required. |
| S | Changed | The vulnerable MCP server used its server-side credentials to act on the separate Pinot cluster security boundary. |
| C | High | Unauthenticated callers could read table data and cluster metadata through server-side Pinot credentials. |
| I | High | Unauthenticated callers could create or update schemas and table configs where the server-side account had those privileges. |
| A | High | Expensive queries and configuration mutations could degrade or disrupt Pinot availability. |

# Unauthenticated tool invocation via default oauth_enabled=False + host 0.0.0.0 bind

## Summary

`mcp-pinot` v3.0.1 (and earlier) defaults to running an HTTP MCP server bound to `0.0.0.0:8080` with no authentication enabled. All MCP tools, including SQL query execution, schema creation, and table-config mutation, are reachable by any network-adjacent caller. The server proxies these calls using server-side Pinot credentials, producing a confused-deputy condition that yields full read/write access to the configured Pinot cluster.

## Affected versions

- All releases on `main`, confirmed in tags v2.1.0 through v3.0.1.
- Affected files: `mcp_pinot/server.py`, `mcp_pinot/config.py`.

## Root cause

Three defaults compose to produce unauthenticated network exposure:

**1. Auth is opt-in and defaults to off** (`mcp_pinot/config.py:64,328`):

```python
@dataclass
class ServerConfig:
    ...
    oauth_enabled: bool = False
    ...

def load_server_config() -> ServerConfig:
    return ServerConfig(
        ...
        oauth_enabled=os.getenv("OAUTH_ENABLED", "false").lower() == "true",
        ...
    )
```

**2. Auth construction is gated by `oauth_enabled`** (`mcp_pinot/server.py:26-46`):

```python
_auth = None
if server_config.oauth_enabled:
    oauth_config = load_oauth_config()
    token_verifier = JWTVerifier(...)
    _auth = OAuthProxy(...)

mcp = FastMCP("Pinot MCP Server", auth=_auth)
```

When `oauth_enabled` is false (default), `_auth` stays `None` and `FastMCP` registers all `@mcp.tool` endpoints with no authentication.

**3. Default bind is all interfaces on a well-known port** (`mcp_pinot/config.py:60-61`):

```python
host: str = "0.0.0.0"
port: int = 8080
```

The HTTP transport in `server.py:263-268` uses these values directly. Any operator following the README's HTTP transport instructions (`uv pip install`, `.env` from `.env.example`, run) ends up with a network-reachable MCP server with no auth.

## Confused-deputy

The Pinot client uses server-side credentials loaded from environment variables (`mcp_pinot/config.py:285-294, 300-315`). When an unauthenticated MCP caller invokes `read_query` or any other tool, the request is executed with the server's `PINOT_TOKEN` or `PINOT_USERNAME`/`PINOT_PASSWORD`, which is typically a privileged service account. The MCP server effectively launders the caller's lack of identity into the server's privileges against the upstream cluster.

## Exposed tools

All 14 tools in `mcp_pinot/server.py` are exposed without auth in the default configuration:

| Tool | Impact when unauthenticated |
|---|---|
| `read_query` | Arbitrary SELECT against any table allowed by server-side filter (or all tables if no filter) |
| `list_tables` | Enumerate cluster schemas |
| `table_details`, `segment_list`, `segment_metadata_details`, `tableconfig_schema_details`, `index_column_details`, `get_schema`, `get_table_config` | Read cluster metadata |
| `create_schema`, `update_schema` | Create or mutate Pinot schemas |
| `create_table_config`, `update_table_config` | Create or mutate table configurations |
| `reload_table_filters` | Reload server filter file; response leaks `previous_filters` and `new_filters` lists |
| `test_connection` | Cluster diagnostics including host, port, scheme, database, and auth-mode |

## Reproduction

Minimal reproduction against a default-configured `mcp-pinot` v3.0.1 instance running on `http://victim:8080/mcp`:

```bash
# 1. Enumerate tables (no Authorization header)
curl -X POST http://victim:8080/mcp \
  -H 'Content-Type: application/json' \
  -d '{
    "jsonrpc":"2.0",
    "method":"tools/call",
    "params":{"name":"list_tables","arguments":{}},
    "id":1
  }'

# 2. Read arbitrary table contents (server forwards using its own Pinot credentials)
curl -X POST http://victim:8080/mcp \
  -H 'Content-Type: application/json' \
  -d '{
    "jsonrpc":"2.0",
    "method":"tools/call",
    "params":{
      "name":"read_query",
      "arguments":{"query":"SELECT * FROM <table> LIMIT 100"}
    },
    "id":2
  }'

# 3. Create a new schema (write privileges)
curl -X POST http://victim:8080/mcp \
  -H 'Content-Type: application/json' \
  -d '{
    "jsonrpc":"2.0",
    "method":"tools/call",
    "params":{
      "name":"create_schema",
      "arguments":{
        "schemaJson":"{\"schemaName\":\"attacker_schema\",\"dimensionFieldSpecs\":[{\"name\":\"id\",\"dataType\":\"STRING\"}]}"
      }
    },
    "id":3
  }'
```

## Severity (CVSS 3.1)

`CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H` = **10.0 Critical**

| Metric | Value | Reason |
|---|---|---|
| AV (Attack Vector) | Network | Server defaults to bind on `0.0.0.0:8080` |
| AC (Attack Complexity) | Low | No special conditions, single HTTP request |
| PR (Privileges Required) | None | No authentication required in default config |
| UI (User Interaction) | None | Direct unauthenticated call |
| S (Scope) | Changed | Vulnerable MCP component grants access to a separate Pinot cluster (different security authority) |
| C (Confidentiality) | High | Full read of any table data the server-side account can reach |
| I (Integrity) | High | Schema and table-config writes via `create_schema`, `update_schema`, `create_table_config`, `update_table_config` |
| A (Availability) | High | Heavy queries, malformed configs, or schema overrides can degrade or break the cluster |

If the operator restricts the bind address to `127.0.0.1` via `MCP_HOST`, AV drops to `Local` and the score reduces. But this is not the documented default.

## Suggested remediation

Two independent hardenings, both recommended:

**A. Refuse to start in an insecure default**, in `server.py` `main()`, fail-closed when:
- `transport != "stdio"`
- `server_config.oauth_enabled` is `False`
- `server_config.host` is not a loopback address (e.g. not in `{"127.0.0.1", "::1", "localhost"}`)

Sample:

```python
def _is_loopback(host: str) -> bool:
    return host in {"127.0.0.1", "::1", "localhost"}

def main():
    ...
    if server_config.transport != "stdio" and not server_config.oauth_enabled and not _is_loopback(server_config.host):
        raise SystemExit(
            "Refusing to start: HTTP transport bound to non-loopback host "
            f"({server_config.host}) without OAuth. Set OAUTH_ENABLED=true or "
            "set MCP_HOST=127.0.0.1 for local-only access."
        )
    ...
```

**B. Default `oauth_enabled` to `True`** and require explicit opt-out for local development. This matches the principle of secure-by-default for network-facing services.

**C. Document the threat model** in README under a "Production deployment" section, including:
- Explicit warning that the server should not be exposed to untrusted networks without OAuth
- Recommendation to set `MCP_HOST=127.0.0.1` for stdio/local-only deployments

## Resources

- `mcp_pinot/server.py` lines 26-46, 248-269
- `mcp_pinot/config.py` lines 56-65, 318-330
- FastMCP `auth` parameter behavior when `None`: https://github.com/jlowin/fastmcp
- The Register, May 13 2026: MCP database flaws across Doris, Pinot, RDS

## Reporter

Independent security researcher. Disclosed via GitHub Security Advisory, 2026-05-23.

## References
- https://github.com/startreedata/mcp-pinot/security/advisories/GHSA-73cv-556c-w3g6
- https://nvd.nist.gov/vuln/detail/CVE-2026-49257
- https://github.com/startreedata/mcp-pinot/issues/90
- https://github.com/startreedata/mcp-pinot/pull/95
- https://github.com/startreedata/mcp-pinot/commit/1c7d3f9cd384854bf72c127d230bdb32299475ad
- https://github.com/startreedata/mcp-pinot
