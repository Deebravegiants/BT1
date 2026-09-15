# [M] OpenClaw: Bundled MCP/LSP tools could bypass configured tool policy

## Summary
Severity: Medium
Advisory: GHSA-qrp5-gfw2-gxv4
CWE: CWE-862
Ecosystem: npm
CVSS: CVSS:4.0/AV:L/AC:L/AT:N/PR:L/UI:N/VC:L/VI:L/VA:N/SC:L/SI:L/SA:N (CVSS_V4)
Published: 2026-04-25
Source: https://github.com/advisories/GHSA-qrp5-gfw2-gxv4
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.4.20

## Details
## Affected Packages / Versions

- Package: `openclaw` (npm)
- Affected versions: `< 2026.4.20`
- Patched version: `2026.4.20`

## Impact

Bundled MCP and LSP tools could be appended to the agent's effective tool set after the normal tool-policy pipeline had already filtered core tools. If an operator configured a restrictive policy, such as a tool profile, explicit allow/deny list, owner-only tool restriction, sandbox tool policy, or subagent tool policy, a bundled MCP/LSP tool could remain available even though the same policy would have denied it.

The issue required a configured bundled MCP or LSP tool source and an operator policy that should have restricted that tool. This was a local agent policy-enforcement bypass, not an unauthenticated remote gateway compromise. Severity is medium.

## Fix

OpenClaw now applies a final effective tool policy pass to bundled MCP/LSP tools before merging them into the tool set used by normal runs and compaction. The pass covers profile policy, provider profile policy, global/agent/group policies, owner-only filtering, sandbox tool policy, and subagent tool policy.

Fix commit:

- `0e7a992d3f3155199c1acc2dd9a53c5b3a4d3ada`

## Release

Fixed in OpenClaw `2026.4.20`.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-qrp5-gfw2-gxv4
- https://github.com/openclaw/openclaw/commit/0e7a992d3f3155199c1acc2dd9a53c5b3a4d3ada
- https://github.com/openclaw/openclaw
