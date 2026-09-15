# [H] mcp-ssh-tool has file transfer path policy bypass and bearer token comparison hardening

## Summary
Severity: High
Advisory: GHSA-j7h9-2jh7-g967
CWE: CWE-208, CWE-22
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-05-07
Source: https://github.com/advisories/GHSA-j7h9-2jh7-g967
Type: github-advisory

## Affected
- npm: `mcp-ssh-tool` — affected >=0 <2.1.1

## Details
## Summary

`mcp-ssh-tool` has released version `2.1.1` with security hardening for transfer path authorization and HTTP bearer authentication.

The release addresses:

- insufficient local path policy enforcement in transfer-related filesystem handling
- incomplete canonicalization and segment-boundary handling for deny-prefix path policy checks
- non-constant-time HTTP bearer token comparison

## Impact

Affected versions may allow policy bypass in transfer path handling under specific configurations, and may expose a timing side channel in bearer-token comparison for HTTP deployments.

## Patched Version

Upgrade to `mcp-ssh-tool >= 2.1.1`.

```bash
npm install -g mcp-ssh-tool@latest
```

## Workarounds

For deployments that cannot immediately upgrade:

- avoid exposing HTTP transport beyond loopback
- use strict filesystem policy configuration
- avoid granting MCP clients access to sensitive local transfer paths
- monitor audit logs for unexpected transfer operations

## Credits

Reported by `dodge1218`.

## References
- https://github.com/oaslananka/mcp-ssh-tool/security/advisories/GHSA-j7h9-2jh7-g967
- https://github.com/oaslananka/mcp-ssh-tool
