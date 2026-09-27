# [M] n8n-MCP: Workflow telemetry sanitizer could retain partial values from URL-shaped node parameters

## Summary
Severity: Medium
Advisory: GHSA-f3rg-xqjj-cj9w
CVE: CVE-2026-45582
CWE: CWE-201
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-05-18
Source: https://github.com/advisories/GHSA-f3rg-xqjj-cj9w
Type: github-advisory

## Affected
- npm: `n8n-mcp` — affected >=0 <2.51.3

## Details
## Summary

In affected versions of n8n-mcp, the workflow telemetry sanitizer could retain partial fragments of URL-shaped node parameters before sending workflow data to the project's anonymous telemetry backend. Values placed in HTTP-Request-style node parameters — such as customer or tenant identifiers, short secrets embedded in query strings, and signed request parameters — could therefore appear in stored telemetry, contrary to the collection boundary documented in `PRIVACY.md`.

## Impact

Operators with access to the project's telemetry backend could read partial fragments of workflow URL parameters that should not have been collected. The bug was scoped to URL-shaped fields in workflow *definitions*; credentials, OAuth tokens, and workflow *execution* data are not affected — credentials are removed by a separate code path, and long secrets and known-provider tokens are matched by dedicated patterns.

## Patches

Fixed in **n8n-mcp `2.51.3`**. Upgrading is the recommended remediation.

## Workarounds

For users who cannot upgrade immediately, disable anonymous telemetry by setting any of these environment variables to `true`:

- `N8N_MCP_TELEMETRY_DISABLED`
- `TELEMETRY_DISABLED`
- `DISABLE_TELEMETRY`

## Credit

Reported by @u-ktdi.

## References
- https://github.com/czlonkowski/n8n-mcp/security/advisories/GHSA-f3rg-xqjj-cj9w
- https://nvd.nist.gov/vuln/detail/CVE-2026-45582
- https://github.com/czlonkowski/n8n-mcp/pull/782
- https://github.com/czlonkowski/n8n-mcp/commit/6cf6fef653fcd6d598f2f356aac4754931c7329f
- https://github.com/czlonkowski/n8n-mcp
- https://github.com/czlonkowski/n8n-mcp/releases/tag/v2.51.3
