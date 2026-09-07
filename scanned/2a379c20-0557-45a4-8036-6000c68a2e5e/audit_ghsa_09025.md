# [H] n8n-MCP: Multi-tenant MCP requests fall back to process-level n8n credentials when tenant headers are absent or incomplete

## Summary
Severity: High
Advisory: GHSA-jxx9-px88-pj69
CVE: CVE-2026-45707
CWE: CWE-284
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-05-18
Source: https://github.com/advisories/GHSA-jxx9-px88-pj69
Type: github-advisory

## Affected
- npm: `n8n-mcp` — affected >=0 <2.51.2

## Details
## Summary

When `ENABLE_MULTI_TENANT=true`, the HTTP transport documents that the target n8n instance is selected per-request from `x-n8n-url` / `x-n8n-key` headers. Requests that omitted those headers — or supplied only one of them — silently fell back to the process-level `N8N_API_URL` / `N8N_API_KEY` credentials configured for the operator's own n8n instance. As a result, an authenticated MCP tenant could cause n8n management calls to execute against the operator's instance instead of its own.

This affects HTTP-mode deployments of `n8n-mcp` that are run as a shared multi-tenant service. Single-tenant deployments (`ENABLE_MULTI_TENANT` unset or `false`) are not affected.

## Impact

An authenticated MCP tenant exploiting this path could read and write workflows, executions, data-table contents, and credential metadata on the operator's n8n instance. If the operator's n8n permits Code-node execution that reaches OS-level modules, the path could escalate to remote code execution inside the operator's n8n runtime. The process-level `N8N_API_KEY` is, in practice, a high-privilege key — Community Edition keys are unscoped by default, and even Enterprise scopes were configured for the operator's own needs and would carry over wholesale to a tenant who triggered the fallback.

## Patches

Fixed in **n8n-mcp 2.51.2**. The fix:

- Rejects header-less multi-tenant requests at the HTTP edge with HTTP 400 / JSON-RPC `-32602` before any handler runs.
- Refuses to construct an env-credential n8n API client when `ENABLE_MULTI_TENANT=true`.
- Closes secondary leak paths in trigger handlers and in the responses of `n8n_health_check`, `n8n_diagnostic`, `n8n_deploy_template`, and `n8n_audit_instance` so the operator's URL and env-key indicator are not surfaced to tenants.

Single-tenant behavior is unchanged.

## Upgrade

```bash
# NPM
npx n8n-mcp@latest

# Docker
docker pull ghcr.io/czlonkowski/n8n-mcp:latest
```

## Workarounds

If an immediate upgrade is not possible, any one of the following reduces or eliminates exposure:

- **Disable multi-tenant mode.** Set `ENABLE_MULTI_TENANT=false` (or unset it) and run a separate n8n-mcp instance per tenant with that tenant's own `N8N_API_URL` / `N8N_API_KEY`. This removes the affected code path entirely.
- **Reject malformed requests at a proxy.** Require both `x-n8n-url` and `x-n8n-key` headers on every request and return 400 if either is missing. Neutralizes the primary header-omission path but does not address the secondary response-shape disclosures, so this is a partial mitigation only.
- **Reduce the blast radius of the operator API key.** If your n8n instance supports API key scoping (Enterprise, or a Community Edition build that exposes scopes), provision the operator's `N8N_API_KEY` with the minimum scopes required for the operator's own n8n-mcp functions. This does not close the boundary break but limits what a falling-back tenant can do.

## Credit

Reported by [@u-ktdi](https://github.com/u-ktdi).

## References
- https://github.com/czlonkowski/n8n-mcp/security/advisories/GHSA-jxx9-px88-pj69
- https://nvd.nist.gov/vuln/detail/CVE-2026-45707
- https://github.com/czlonkowski/n8n-mcp/commit/853015d0897be7cf2d9d4726de195c938e4395ab
- https://github.com/czlonkowski/n8n-mcp
- https://github.com/czlonkowski/n8n-mcp/releases/tag/v2.51.2
