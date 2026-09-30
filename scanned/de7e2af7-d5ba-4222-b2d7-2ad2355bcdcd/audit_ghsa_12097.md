# [M] OpenClaw's Discord component interaction ingress skips guild/channel policy enforcement

## Summary
Severity: Medium
Advisory: GHSA-jp4j-q5fc-58gv
CWE: CWE-862
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:L/VA:N/SC:N/SI:L/SA:N (CVSS_V4)
Published: 2026-03-31
Source: https://github.com/advisories/GHSA-jp4j-q5fc-58gv
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=2026.2.14 <2026.3.28

## Details
## Summary

Discord button and component interaction ingress did not consistently reapply the same guild and channel policy gates used for normal inbound messages.

## Impact

Users could trigger privileged component actions from contexts that should have been blocked by Discord channel policy.

## Affected Component

`extensions/discord/src/monitor/agent-components.ts`

## Fixed Versions

- Affected: `>= 2026.2.14, <= 2026.3.24`
- Patched: `>= 2026.3.28`
- Latest stable `2026.3.28` contains the fix.

## Fix

Fixed by commit `511093d4b3` (`Discord: apply component interaction policy gates`).

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-jp4j-q5fc-58gv
- https://github.com/openclaw/openclaw/commit/511093d4b37c0831c778fabd25ec3020834983c3
- https://github.com/openclaw/openclaw
- https://github.com/openclaw/openclaw/releases/tag/v2026.3.28
