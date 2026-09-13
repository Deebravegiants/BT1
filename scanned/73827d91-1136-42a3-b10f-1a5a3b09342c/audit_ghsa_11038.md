# [H] OpenClaw: Gateway `agent` calls could override the workspace boundary

## Summary
Severity: High
Advisory: GHSA-2rqg-gjgv-84jm
CWE: CWE-668
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-03-13
Source: https://github.com/advisories/GHSA-2rqg-gjgv-84jm
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.3.11

## Details
### Summary

The public gateway `agent` RPC allowed an authenticated operator with `operator.write` to supply attacker-controlled `spawnedBy` and `workspaceDir` values. That let the caller re-root the agent run outside its configured workspace boundary.

### Impact

A non-owner operator could escape the intended workspace boundary and run normal file and exec tools from an arbitrary process-accessible directory.

### Affected versions

`openclaw` `<= 2026.3.8`

### Patch

Fixed in `openclaw` `2026.3.11` and included in later releases such as `2026.3.12`. The gateway now enforces the configured workspace boundary for agent runs regardless of caller-supplied overrides.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-2rqg-gjgv-84jm
- https://github.com/openclaw/openclaw
- https://github.com/openclaw/openclaw/releases/tag/v2026.3.11
