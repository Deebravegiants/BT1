# [H] OpenClaw's Trusted-proxy Control UI sessions retain privileged scopes without device identity on device-less allow paths

## Summary
Severity: High
Advisory: GHSA-48vw-m3qc-wr99
Ecosystem: npm
Published: 2026-03-26
Source: https://github.com/advisories/GHSA-48vw-m3qc-wr99
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.3.22

## Details
## Summary
Trusted-proxy Control UI sessions without device identity could retain self-declared privileged scopes on the device-less allow path.

## Affected Packages / Versions
- Package: `openclaw` (npm)
- Affected: < 2026.3.22
- Fixed: >= 2026.3.22
- Latest released tag checked: `v2026.3.23-2` (`630f1479c44f78484dfa21bb407cbe6f171dac87`)
- Latest published npm version checked: `2026.3.23-2`

## Fix Commit(s)
- `ccf16cd8892402022439346ae1d23352e3707e9e`

## Release Status
The fix shipped in `v2026.3.22` and remains present in `v2026.3.23` and `v2026.3.23-2`.

## Code-Level Confirmation
- src/gateway/server/ws-connection/message-handler.ts now strips unbound self-declared scopes on the trusted-proxy no-device path.
- src/gateway/server/ws-connection/connect-policy.ts remains the allow path, but the shipped scope scrub prevents privilege retention without device identity.

OpenClaw thanks @nexrin for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-48vw-m3qc-wr99
- https://github.com/openclaw/openclaw/commit/ccf16cd8892402022439346ae1d23352e3707e9e
- https://github.com/openclaw/openclaw
