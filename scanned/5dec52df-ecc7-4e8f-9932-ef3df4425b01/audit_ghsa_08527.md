# [H] dynoxide: DNS rebinding and cross-origin CSRF via MCP HTTP transport

## Summary
Severity: High
Advisory: GHSA-fvh2-gm75-j4j7
CWE: CWE-346, CWE-350, CWE-352
Ecosystem: crates.io, npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-05-18
Source: https://github.com/advisories/GHSA-fvh2-gm75-j4j7
Type: github-advisory

## Affected
- crates.io: `dynoxide-rs` — affected >=0.9.3 <0.9.13
- npm: `dynoxide` — affected >=0.9.3 <0.9.13

## Details
## Summary

dynoxide's MCP HTTP transport was vulnerable to DNS rebinding via its transitive `rmcp` dependency, plus a related cross-origin CSRF gap. A malicious web page could make the user's browser send requests to a local `dynoxide mcp --http` or `dynoxide serve --mcp` server with a non-loopback `Host` header, which the server would then process. Affects 0.9.3 to 0.9.12. The stdio transport (`dynoxide mcp` without `--http`, which is the default) is not affected.

## Impact

If a user is running `dynoxide mcp --http` (or `dynoxide serve --mcp`) on their machine and then visits a malicious web page, the attacker's JavaScript can call any MCP tool exposed by the running dynoxide instance.

Reachable tools include reads (`get_item`, `query`, `scan`, `batch_get_item`, `describe_table`, `list_tables`) and writes (`put_item`, `update_item`, `delete_item`, `create_table`, `batch_write_item`).

Any data in tables that the local dynoxide instance has access to can be read, modified, or destroyed.

## Patches

dynoxide 0.9.13 closes both the named CVE and a related cross-origin CSRF gap:

1. **DNS rebinding (the named CVE).** `rmcp` is upgraded from 1.1.1 to 1.6.0. rmcp 1.4+ ships a default Host-header allowlist (`["localhost", "127.0.0.1", "::1"]`) which rejects requests carrying any other Host header with a 403.

2. **Defence in depth.** Explicit `allowed_hosts` and `allowed_origins` lists are now set on `StreamableHttpServerConfig` directly. The Host allowlist protects against a future rmcp default flip. The Origin allowlist closes a related cross-origin CSRF gap that the Host check alone does not address: a malicious page could `fetch` the loopback endpoint with `mode: 'no-cors'`, the Host header would match (it's the literal loopback address the browser is connecting to), but the Origin header would otherwise have been unchecked.

Native MCP clients that don't send an Origin header (Claude Code, Cursor, the dynoxide CLI) are unaffected by the Origin check and continue to work.

## Workarounds

- Upgrade to dynoxide 0.9.13.
- If upgrade is not immediately possible: do not run the MCP HTTP transport. Run `dynoxide mcp` (stdio, the default) instead of `dynoxide mcp --http`, and don't pass `--mcp` to `dynoxide serve`.

## Resources

- Upstream rmcp advisory: [GHSA-89vp-x53w-74fx](https://github.com/modelcontextprotocol/rust-sdk/security/advisories/GHSA-89vp-x53w-74fx)
- Upstream CVE: [CVE-2026-42559](https://www.cve.org/CVERecord?id=CVE-2026-42559)
- dynoxide release: [v0.9.13](https://github.com/nubo-db/dynoxide/releases/tag/v0.9.13)
- MCP transport security guidance: <https://modelcontextprotocol.io/specification/2025-11-25/basic/transports#security-warning>

## Credits

Vulnerability identified via GitHub Dependabot alert on the transitive rmcp dependency.

## References
- https://github.com/nubo-db/dynoxide/security/advisories/GHSA-fvh2-gm75-j4j7
- https://github.com/nubo-db/dynoxide
- https://github.com/nubo-db/dynoxide/releases/tag/v0.9.13
- https://rustsec.org/advisories/RUSTSEC-2026-0140.html
