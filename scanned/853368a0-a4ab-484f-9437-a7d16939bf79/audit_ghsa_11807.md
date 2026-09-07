# [M] OpenClaw has agent avatar symlink traversal in gateway session metadata

## Summary
Severity: Medium
Advisory: GHSA-9mph-4f7v-fmvh
CWE: CWE-59
Ecosystem: npm
CVSS: CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-04
Source: https://github.com/advisories/GHSA-9mph-4f7v-fmvh
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.2.22

## Details
## Summary
A crafted local avatar path could follow a symlink outside the agent workspace and return arbitrary file contents as a base64 `data:` URL in gateway responses.

## Impact
- Confidentiality impact: local file read in the gateway process context.
- Exfiltration path: `agents.list` can return the resulting `avatarUrl` payload.

## Affected Components
- `src/gateway/session-utils.ts` (`resolveIdentityAvatarUrl`)

## Affected Packages / Versions
- Package: `openclaw` (npm)
- Introduced: `v2026.1.21`
- Affected published versions: `<= 2026.2.21-2`
- Planned patched version: `2026.2.22`

## Remediation
- Resolve workspace and avatar paths with `realpath` and enforce realpath containment.
- Open files with `O_NOFOLLOW` when available.
- Compare pre-open and opened file identity (`dev`/`ino`) to block swap races.
- Add regression tests for outside-workspace symlink rejection and in-workspace symlink allowance.

## Fix Commit(s)
- `3d0337504349954237d09e4d957df5cb844d5e77`

OpenClaw thanks @aether-ai-agent for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-9mph-4f7v-fmvh
- https://github.com/openclaw/openclaw/commit/3d0337504349954237d09e4d957df5cb844d5e77
- https://github.com/openclaw/openclaw
