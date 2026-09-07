# [M] OpenClaw: Write-scoped callers could reach admin-only session reset logic through `agent`

## Summary
Severity: Medium
Advisory: GHSA-jf6w-m8jw-jfxc
CWE: CWE-863
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:H (CVSS_V3)
Published: 2026-03-13
Source: https://github.com/advisories/GHSA-jf6w-m8jw-jfxc
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.3.11

## Details
## Summary
In affected versions of `openclaw`, a gateway caller with `operator.write` could issue `agent` requests containing `/new` or `/reset` and reach the same reset path used by the admin-only `sessions.reset` RPC.

## Impact
On gateways where a caller is intentionally granted `operator.write` but not `operator.admin`, that caller could reset targeted conversation state through `agent` slash commands. This crosses the documented method-scope boundary between write-scoped messaging and admin-only session mutation.

## Affected Packages and Versions
- Package: `openclaw` (npm)
- Affected versions: `<= 2026.3.8`
- Fixed in: `2026.3.11`

## Technical Details
Scope checks were enforced only on the outer RPC method. The `agent` slash-command path reused admin-only reset logic internally, so a write-scoped caller could reach session-reset mutation without holding `operator.admin`.

## Fix
OpenClaw no longer routes conversation `/new` and `/reset` through the admin-only `sessions.reset` entry point. Reset logic now lives in a shared service, while `sessions.reset` remains admin-only. The fix shipped in `openclaw@2026.3.11`.

## Workarounds
Upgrade to `2026.3.11` or later.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-jf6w-m8jw-jfxc
- https://github.com/openclaw/openclaw
- https://github.com/openclaw/openclaw/releases/tag/v2026.3.11
