# [H] OpenClaw's device removal and token revocation do not terminate active WebSocket sessions

## Summary
Severity: High
Advisory: GHSA-2pr2-hcv6-7gwv
CVE: CVE-2026-34503
CWE: CWE-613
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-03-31
Source: https://github.com/advisories/GHSA-2pr2-hcv6-7gwv
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.3.28

## Details
## Summary

Removing a device or revoking its token updated stored credentials but did not disconnect already-authenticated WebSocket sessions.

## Impact

A revoked device could continue using its existing live session until reconnect, extending access beyond credential removal.

## Affected Component

`src/gateway/server-methods/devices.ts, src/gateway/server.impl.ts`

## Fixed Versions

- Affected: `<= 2026.3.24`
- Patched: `>= 2026.3.28`
- Latest stable `2026.3.28` contains the fix.

## Fix

Fixed by commit `7a801cc451` (`Gateway: disconnect revoked device sessions`).

OpenClaw thanks @AntAISecurityLab for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-2pr2-hcv6-7gwv
- https://nvd.nist.gov/vuln/detail/CVE-2026-34503
- https://github.com/openclaw/openclaw/commit/7a801cc451e9e667b705eeccff651923a1b8c863
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-incomplete-websocket-session-termination-on-device-removal-and-token-revocation
