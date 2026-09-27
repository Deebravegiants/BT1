# [H] OpenClaw: Gateway chat.send ACP-only provenance guard could be bypassed by client identity spoofing

## Summary
Severity: High
Advisory: GHSA-6xg4-82hv-cp6f
CVE: CVE-2026-41299
CWE: CWE-290, CWE-807
Ecosystem: npm
Published: 2026-03-31
Source: https://github.com/advisories/GHSA-6xg4-82hv-cp6f
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.3.28

## Details
## Summary

ACP-only provenance fields in `chat.send` were gated by self-declared client metadata from the WebSocket handshake rather than verified authorization state.

## Impact

A normal authenticated operator client could spoof ACP identity labels and inject reserved provenance fields intended only for the ACP bridge.

## Affected Component

`src/gateway/server-methods/chat.ts, src/gateway/server/ws-connection/message-handler.ts`

## Fixed Versions

- Affected: `<= 2026.3.24`
- Patched: `>= 2026.3.28`
- Latest stable `2026.3.28` contains the fix.

## Fix

Fixed by commit `4b9542716c` (`Gateway: require verified scope for chat provenance`).

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-6xg4-82hv-cp6f
- https://github.com/openclaw/openclaw/commit/4b9542716c26ac77652bcaa0f562043b298b409f
- https://github.com/openclaw/openclaw
