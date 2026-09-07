# [H] atomic-agents-stack: HTTP MCP catalog accepts cleartext http and spawns catalog-supplied commands (MITM to RCE)

## Summary
Severity: High
Advisory: GHSA-xhcr-cqfr-m3hv
CWE: CWE-319, CWE-494
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-08-17
Source: https://github.com/advisories/GHSA-xhcr-cqfr-m3hv
Type: github-advisory

## Affected
- PyPI: `atomic-agents-stack` — affected >=0 <1.1.0

## Details
The HTTP MCP server-registry backend factory (`atomic_agents/mcp_registry/http.py`, `make_http_mcp_server_registry_backend_from_url`) accepts both `http` and `https` schemes. Catalog entries carry `command`/`args` that are type-validated but content-unrestricted, and are later spawned as local stdio subprocesses by `MCPClientPool`. Over a cleartext `http://` catalog URL, a network man-in-the-middle can rewrite the catalog response to inject an arbitrary `command`/`args` and obtain code execution on the agent host, with no LLM involvement. The Policy MCP allowlist is not a default mitigation (`mcp_allow_fn` defaults to None), so absent an operator-authored allowlist every resolved spec connects.

**Affected:** `mcp_registry/http.py`, all versions through 1.0.0. (The `https` path is sound: `httpx` defaults to `verify=True`, `follow_redirects=False`.)

**Fix:** require `https` by default and gate `http://` behind a loud explicit opt-in. Defense-in-depth: allowlist the resolved command basename (or require confirmation) before any registry-sourced subprocess spawn. Document the consequence in spec/36.

## References
- https://github.com/dep0we/atomic-agents-stack/security/advisories/GHSA-xhcr-cqfr-m3hv
- https://github.com/dep0we/atomic-agents-stack
- https://github.com/dep0we/atomic-agents-stack/releases#release-v1.1.0
