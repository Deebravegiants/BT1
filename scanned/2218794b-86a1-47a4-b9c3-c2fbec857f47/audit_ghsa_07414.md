# [C] n8n-MCP: Cross-tenant access to workflow version backups in multi-tenant HTTP deployments

## Summary
Severity: Critical
Advisory: GHSA-j6r7-6fhx-77wx
CVE: CVE-2026-54052
CWE: CWE-639, CWE-862
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:L (CVSS_V3)
Published: 2026-07-14
Source: https://github.com/advisories/GHSA-j6r7-6fhx-77wx
Type: github-advisory

## Affected
- npm: `n8n-mcp` — affected >=0 <2.56.1

## Details
## Impact

In multi-tenant HTTP deployments — where a single n8n-mcp server serves several tenants — the locally stored workflow version history (the automatic backups taken before workflow updates) was not isolated per tenant. An authenticated tenant could read workflow version snapshots belonging to other tenants, and could delete or destroy other tenants' stored backups.

A stored snapshot includes full node definitions, so the exposed data can contain credential references and authorization headers configured on nodes. This is therefore a confidentiality issue in addition to an integrity/availability one.

## Affected configurations

- HTTP mode with multi-tenancy enabled (`ENABLE_MULTI_TENANT=true`), where multiple tenants are served by a single shared instance and database.

Not affected:

- stdio / single-user deployments (e.g. Claude Desktop).
- Single-tenant HTTP deployments (one tenant per instance and database).

## Affected versions

`<= 2.56.0`

## Patched version

`2.56.1`. The stored version history is now isolated per instance, so a tenant can only access its own backups. Upgrading runs a one-time migration that isolates existing history and clears previously stored, un-scoped backups (these are auto-created, short-retention backups).

## Workarounds

If users cannot upgrade immediately:

- Disable the workflow version tool by setting `DISABLED_TOOLS=n8n_workflow_versions` in the server environment (for example, in your Docker `.env`). This removes the affected tool from the deployment for all tenants; automatic backups are unaffected, but the cross-tenant access path is closed.
- Alternatively, do not run in multi-tenant mode — serve each tenant from a separate instance with its own database, so no local store is shared between tenants.
- Restrict network access to the HTTP endpoint to trusted operators.

stdio and single-tenant HTTP deployments are not affected.

## Credit

Reported by Francisco Rosales (@0xmagic0) and coordinated by Ax Sharma (@axsharma) of Manifold Security.

## References
- https://github.com/czlonkowski/n8n-mcp/security/advisories/GHSA-j6r7-6fhx-77wx
- https://github.com/czlonkowski/n8n-mcp
- https://github.com/czlonkowski/n8n-mcp/releases/tag/v2.56.1
