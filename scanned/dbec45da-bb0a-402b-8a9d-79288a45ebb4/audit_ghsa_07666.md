# [H] OpenClaw Hook Session Key Override Enables Targeted Cross-Session Routing

## Summary
Severity: High
Advisory: GHSA-hv93-r4j3-q65f
CWE: CWE-330, CWE-639
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:H/A:N (CVSS_V3)
Published: 2026-02-17
Source: https://github.com/advisories/GHSA-hv93-r4j3-q65f
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=2.0.0-beta3 <2026.2.12

## Details
## Summary
The issue is not deterministic session keys by itself. The exploitable path was accepting externally supplied `sessionKey` values on authenticated hook ingress, allowing a hook token holder to route messages into chosen sessions.

## Affected Behavior
- `POST /hooks/agent` accepted payload `sessionKey` and used it directly for session routing.
- Common session-key shapes (for example `agent:main:dm:<peerId>`) were often derivable from known metadata, making targeted routing practical when request-level override was enabled.

## Attack Preconditions
- Attacker can call hook endpoints with a valid hook token.
- Hook ingress allows request-selected `sessionKey` values.
- Target session keys can be derived or guessed.

Without those preconditions, deterministic key formats alone do not provide access.

## Impact
- Integrity: targeted message/prompt injection into chosen sessions.
- Persistence: poisoned context can affect subsequent turns when the same session key is reused.
- Confidentiality impact is secondary and depends on additional weaknesses.

## Affected Versions
- `openclaw` `>= 2.0.0-beta3` and `< 2026.2.12`

## Patched Versions
- `openclaw` `>= 2026.2.12`

## Fix
OpenClaw now uses secure defaults for hook session routing:
- `POST /hooks/agent` rejects payload `sessionKey` unless `hooks.allowRequestSessionKey=true`.
- Added `hooks.defaultSessionKey` for fixed ingress routing.
- Added `hooks.allowedSessionKeyPrefixes` to constrain explicit routing keys.
- Security audit warns on unsafe hook session-routing settings.

## Recommended Configuration
```json
{
  "hooks": {
    "enabled": true,
    "token": "${OPENCLAW_HOOKS_TOKEN}",
    "defaultSessionKey": "hook:ingress",
    "allowRequestSessionKey": false,
    "allowedSessionKeyPrefixes": ["hook:"]
  }
}
```

## Credit
Thanks @alpernae for responsible reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-hv93-r4j3-q65f
- https://github.com/openclaw/openclaw/commit/113ebfd6a23c4beb8a575d48f7482593254506ec
- https://github.com/openclaw/openclaw
- https://github.com/openclaw/openclaw/releases/tag/v2026.2.12
