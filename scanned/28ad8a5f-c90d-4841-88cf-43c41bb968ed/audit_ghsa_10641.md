# [H] OpenClaw Gateway `operator.write` can reach admin-only session reset via `chat.send` `/reset`

## Summary
Severity: High
Advisory: GHSA-5r8f-96gm-5j6g
CWE: CWE-284, CWE-863
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:H/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-04-01
Source: https://github.com/advisories/GHSA-5r8f-96gm-5j6g
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.3.28

## Details
## Summary

The `chat.send` path reused command authorization to trigger `/reset` session rotation even though direct session reset is an admin-only control-plane operation.

## Impact

A write-scoped gateway caller could rotate a target session, archive the prior transcript state, and force a new session id without admin scope.

## Affected Component

`src/gateway/server-methods/chat.ts, src/auto-reply/reply/session.ts`

## Fixed Versions

- Affected: `<= 2026.3.24`
- Patched: `>= 2026.3.28`
- Latest stable `2026.3.28` contains the fix.

## Fix

Fixed by commit `be00fcfccb` (`Gateway: align chat.send reset scope checks`).

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-5r8f-96gm-5j6g
- https://github.com/openclaw/openclaw/commit/be00fcfccba108f88dc3d4380146c6e058770b03
- https://github.com/openclaw/openclaw
- https://github.com/openclaw/openclaw/releases/tag/v2026.3.28
