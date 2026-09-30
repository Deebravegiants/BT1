# [H] OpenClaw: Leaf subagents could steer sibling sessions across sandbox boundaries

## Summary
Severity: High
Advisory: GHSA-4w7m-58cg-cmff
CWE: CWE-269
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-03-13
Source: https://github.com/advisories/GHSA-4w7m-58cg-cmff
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.3.11

## Details
## Summary
In affected versions of `openclaw`, sandboxed leaf subagents could still access the `subagents` control surface and resolve against the parent requester scope instead of remaining confined to their own session tree.

## Impact
A low-privilege sandboxed leaf worker could steer or kill a sibling run owned by the same requester and cause that sibling to execute with its own broader tool policy. This is a sandbox and session-scope boundary bypass.

## Affected Packages and Versions
- Package: `openclaw` (npm)
- Affected versions: `<= 2026.3.8`
- Fixed in: `2026.3.11`

## Technical Details
Leaf subagents retained the `subagents` tool, and subagent control requests were authorized against the parent requester scope rather than the caller's own spawned descendants. The control path prevented only self-targeting, not cross-sibling steering.

## Fix
OpenClaw now removes `subagents` control access from leaf subagents by default, scopes subagent control to the caller's own descendants, and rejects `steer` and `kill` requests that target runs outside that descendant tree. The fix shipped in `openclaw@2026.3.11`.

## Workarounds
Upgrade to `2026.3.11` or later.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-4w7m-58cg-cmff
- https://github.com/openclaw/openclaw
- https://github.com/openclaw/openclaw/releases/tag/v2026.3.11
