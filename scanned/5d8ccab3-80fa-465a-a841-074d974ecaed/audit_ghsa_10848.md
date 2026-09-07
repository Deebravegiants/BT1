# [H] OpenClaw's mutating internal ACP chat commands missed operator.admin scope enforcement

## Summary
Severity: High
Advisory: GHSA-3w6x-gv34-mqpf
CWE: CWE-862
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-26
Source: https://github.com/advisories/GHSA-3w6x-gv34-mqpf
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.3.22

## Details
## Summary
Mutating internal ACP chat commands missed the operator.admin gate that should separate read-only and mutating control-plane actions.

## Affected Packages / Versions
- Package: `openclaw` (npm)
- Affected: < 2026.3.22
- Fixed: >= 2026.3.22
- Latest released tag checked: `v2026.3.23-2` (`630f1479c44f78484dfa21bb407cbe6f171dac87`)
- Latest published npm version checked: `2026.3.23-2`

## Fix Commit(s)
- `229426a257e49694a59fa4e3895861d02a4d767f`

## Release Status
The fix shipped in `v2026.3.22` and remains present in `v2026.3.23` and `v2026.3.23-2`.

## Code-Level Confirmation
- src/auto-reply/reply/commands-acp.ts now requires operator.admin for mutating internal ACP actions.
- src/auto-reply/reply/commands-acp.test.ts ships regression coverage for non-admin denial and admin success cases.

OpenClaw thanks @tdjackey for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-3w6x-gv34-mqpf
- https://github.com/openclaw/openclaw/commit/229426a257e49694a59fa4e3895861d02a4d767f
- https://github.com/openclaw/openclaw
