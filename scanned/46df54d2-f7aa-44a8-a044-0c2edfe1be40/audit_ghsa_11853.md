# [M] OpenClaw's Zalouser allowlist authorization matched mutable group names by default

## Summary
Severity: Medium
Advisory: GHSA-f5mf-3r52-r83w
CWE: CWE-807, CWE-863
Ecosystem: npm
Published: 2026-03-13
Source: https://github.com/advisories/GHSA-f5mf-3r52-r83w
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.3.12

## Details
### Summary

OpenClaw's Zalouser allowlist mode accepted mutable group names and normalized slugs as authorization matches instead of requiring stable group IDs. In deployments that used name-based `channels.zalouser.groups` entries together with permissive sender allowlists, a different group could be accepted by reusing the same display name as an allowlisted group.

### Impact

This weakened channel authorization for Zalouser group routing and could allow messages from an unintended group to reach the agent when operators relied on group names instead of stable IDs.

### Affected versions

`openclaw` `<= 2026.3.11`

### Patch

Fixed in `openclaw` `2026.3.12`. Allowlist authorization now matches stable group identifiers, and users should update to `2026.3.12` or later.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-f5mf-3r52-r83w
- https://github.com/openclaw/openclaw
- https://github.com/openclaw/openclaw/releases/tag/v2026.3.12
