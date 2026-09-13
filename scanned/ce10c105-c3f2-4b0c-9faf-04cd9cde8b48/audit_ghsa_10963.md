# [M] OpenClaw's elevated allowFrom accepted broader identity signals than specified within sender-scoped authorization

## Summary
Severity: Medium
Advisory: GHSA-f6h3-846h-2r8w
CWE: CWE-639
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-04
Source: https://github.com/advisories/GHSA-f6h3-846h-2r8w
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.2.22

## Details
### Summary
In certain elevated-mode configurations, `tools.elevated.allowFrom` accepted broader identity signals than intended. The fix tightens matching to sender-scoped identity by default and makes mutable metadata matching explicit.

### Context
OpenClaw is commonly used in 1:1 chats or trusted group chats. In that intended model, this issue is best treated as authorization hardening / defense-in-depth for elevated sender approval.

### Affected Packages / Versions
- Package: `openclaw` (npm)
- Latest published npm version at triage: `2026.2.21-2`
- Affected versions: `<= 2026.2.21-2`
- Planned patched version (pre-set for publish-ready advisory): `2026.2.22`

### Details
Elevated sender authorization now matches sender-scoped identity values only by default (`SenderId`, `From`, `SenderE164`) and no longer considers recipient routing fields such as `ctx.To`.

Mutable sender metadata (`SenderName`, `SenderUsername`, `SenderTag`) now requires explicit allowlist prefixes (`name:`, `username:`, `tag:`). Explicit identity prefixes are also supported (`id:`, `from:`, `e164:`).

### Fix Commit(s)
- `6817c0ec7b4fa830123d4f5c340f075a4bd04ee2`

### Release Process Note
The advisory `patched_versions` is pre-set to the planned next release (`2026.2.22`). Once npm `openclaw@2026.2.22` is published, this advisory can be published without additional content edits.

OpenClaw thanks @jiseoung for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-f6h3-846h-2r8w
- https://github.com/openclaw/openclaw/commit/6817c0ec7b4fa830123d4f5c340f075a4bd04ee2
- https://github.com/openclaw/openclaw
