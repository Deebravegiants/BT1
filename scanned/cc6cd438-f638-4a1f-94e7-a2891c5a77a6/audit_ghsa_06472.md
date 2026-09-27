# [M] n8n-MCP: Incorrect authorization can expose default-scope workflow version backups in multi-tenant HTTP mode

## Summary
Severity: Medium
Advisory: GHSA-2cf7-hpwf-47h9
CVE: CVE-2026-55608
CWE: CWE-200, CWE-863
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-07-14
Source: https://github.com/advisories/GHSA-2cf7-hpwf-47h9
Type: github-advisory

## Affected
- npm: `n8n-mcp` — affected >=0 <2.57.4

## Details
## Summary

In multi-tenant HTTP mode (`ENABLE_MULTI_TENANT=true`), an authenticated tenant could, under certain conditions, reach n8n-mcp's local default-scope `workflow_versions` backups instead of being confined to its own tenant scope. This affects n8n-mcp's own local workflow-version storage, not a normal n8n API capability.

## Impact

An authenticated MCP HTTP tenant could read or delete workflow-version backups stored in the default (single-tenant) scope — for example backups left from a prior single-tenant deployment or a migration period. Workflow snapshots may contain sensitive workflow configuration depending on their contents. Single-tenant and stdio deployments are not affected.

## Affected versions

`<= 2.57.3`

## Patched version

`2.57.4`

## Remediation

Upgrade to n8n-mcp `2.57.4` or later. The fix requires a complete tenant context in multi-tenant mode and fails closed for workflow-version access that cannot be attributed to a specific tenant.

## Workarounds

- Restrict network access to the HTTP endpoint (firewall / reverse proxy / VPN) so only trusted callers can reach it.
- Run in stdio mode, which has no multi-tenant HTTP surface.
- If default-scope backups from a prior single-tenant deployment are not needed, removing them eliminates the exposure.

## Credit

Reported by @DavidCarliez.

## References
- https://github.com/czlonkowski/n8n-mcp/security/advisories/GHSA-2cf7-hpwf-47h9
- https://github.com/czlonkowski/n8n-mcp/commit/c1ca1e73697feaec5ec2a5fb7e6992a2892b62c9
- https://github.com/czlonkowski/n8n-mcp
- https://github.com/czlonkowski/n8n-mcp/releases/tag/v2.57.4
