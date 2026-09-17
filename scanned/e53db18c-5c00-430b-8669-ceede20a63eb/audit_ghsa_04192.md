# [H] mcp-memory-service: OAuth read-only clients can write and delete memories through MCP tools/call

## Summary
Severity: High
Advisory: GHSA-2r68-g678-7qr3
CVE: CVE-2026-49291
CWE: CWE-862
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:H (CVSS_V3)
Published: 2026-06-26
Source: https://github.com/advisories/GHSA-2r68-g678-7qr3
Type: github-advisory

## Affected
- PyPI: `mcp-memory-service` — affected >=0 <10.65.3

## Details
## Summary

The HTTP MCP JSON-RPC endpoint at `/mcp` requires only OAuth `read` scope for all requests, then dispatches `tools/call` directly to handlers that include mutating tools. A read-only OAuth client can call `store_memory` and `delete_memory` through MCP even though the corresponding REST endpoints require `write` scope.

## Technical Details

`src/mcp_memory_service/web/api/mcp.py` declares `mcp_endpoint` with `user: AuthenticationResult = Depends(require_read_access)`. For `tools/call`, it extracts the requested tool name and arguments, then calls `handle_tool_call(storage, tool_name, arguments)` without passing the authenticated user or checking a per-tool required scope.

The MCP tool registry includes both read tools and write tools. In the same handler file, `store_memory` creates a `Memory` object and calls `storage.store(...)`, while `delete_memory` calls `storage.delete(content_hash)`. These operations are reachable with only the `read` scope.

The REST endpoint demonstrates the intended boundary: `POST /api/memories` uses `Depends(require_write_access)` and rejects a read-only token with 403 `insufficient_scope`.

## Reproduction

1. Enable OAuth and disable anonymous access.
2. Generate a valid OAuth JWT with only `scope: read`.
3. Confirm the REST write endpoint rejects it:

```http
POST /api/memories
Authorization: Bearer <read-only-token>
Content-Type: application/json

{"content":"rest denied control"}
```

Expected and observed: HTTP 403 with `Required scope 'write' not granted`.

4. Send the same read-only token to the MCP endpoint:

```http
POST /mcp
Authorization: Bearer <read-only-token>
Content-Type: application/json

{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "store_memory",
    "arguments": {
      "content": "mcp read scope stored this",
      "tags": ["poc"]
    }
  }
}
```

Observed: HTTP 200 JSON-RPC success and the storage `store` sink is reached.

5. A read-only token can also call `delete_memory` through MCP if it knows a content hash:

```http
POST /mcp
Authorization: Bearer <read-only-token>
Content-Type: application/json

{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "tools/call",
  "params": {
    "name": "delete_memory",
    "arguments": {"content_hash": "<known_hash>"}
  }
}
```

Observed: HTTP 200 JSON-RPC success and the storage `delete` sink is reached.

## Impact

A client intended to be read-only can inject or delete memories through the MCP API. This can corrupt the memory database, influence future agent context, and destroy stored user memories without the OAuth `write` scope required by the REST API.

## Affected Versions

Confirmed present on current main commit `c99a922477df41f75a44db11182ae48a57311910` and latest release tag `v10.65.0` (`4eb4a62665589f9dd9f8c393afa32de434b4098a`).

## Suggested Fix

Enforce authorization per MCP tool at `tools/call` time. Require `write` for `store_memory` and `delete_memory`, keep `read` only for read-only tools, and add regression tests proving direct `tools/call` to mutating tools is rejected before the handler reaches storage when the caller has only `read` scope.

## References
- https://github.com/doobidoo/mcp-memory-service/security/advisories/GHSA-2r68-g678-7qr3
- https://nvd.nist.gov/vuln/detail/CVE-2026-49291
- https://github.com/doobidoo/mcp-memory-service
- https://pypi.org/project/mcp-memory-service/10.65.3
- https://web.archive.org/web/20260508112116/https://github.com/doobidoo/mcp-memory-service
