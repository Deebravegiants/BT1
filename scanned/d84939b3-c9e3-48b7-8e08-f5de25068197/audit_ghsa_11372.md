# [M] OpenClaw: `operator.write` chat.send could reach admin-only config writes

## Summary
Severity: Medium
Advisory: GHSA-hfpr-jhpq-x4rm
CWE: CWE-863
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2026-03-09
Source: https://github.com/advisories/GHSA-hfpr-jhpq-x4rm
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.3.7

## Details
### Summary
A gateway client authenticated with `operator.write` could route `/config set` or `/config unset` through `chat.send` and reach persistent config mutation even though direct config RPC methods are admin-scoped.

### Affected Packages / Versions
- Package: `openclaw` (npm)
- Latest published vulnerable version: `2026.3.2`
- Affected range: `<= 2026.3.2`
- Patched in: `2026.3.7`

### Details
Before the fix, `chat.send` ran slash commands in an internal gateway-chat context with `CommandAuthorized: true`, and `/config` write paths only checked command authorization plus `commands.config` / `channels.<provider>.configWrites` gates. That allowed an authenticated `operator.write` gateway client to bridge into persistent config writes even though direct `config.*` RPC methods remain `operator.admin` scoped.

The fix keeps command functionality intact while restoring the intended scope boundary:
- persistent `/config set|unset` writes routed through gateway `chat.send` now require `operator.admin`
- read-only `/config show` remains available to normal write-scoped gateway clients
- normal messaging-channel `/config` behavior remains unchanged

### Impact
This is a real authorization mismatch, but exploitability requires an already authenticated gateway client with `operator.write`, `chat.send` access, and `/config` command support enabled. Maintainer severity is set to medium because the bug is a scoped control-plane privilege mismatch rather than a broad unauthenticated or generic remote compromise. The main consequence is unintended persistent config mutation.

### Fix Commit(s)
- `5f8f58ae25e2a78f31b06edcf26532d634ca554e`

### Release Process Note
npm `2026.3.7` was published on March 8, 2026. This advisory is fixed in the released package.

Thanks @tdjackey for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-hfpr-jhpq-x4rm
- https://github.com/openclaw/openclaw/commit/5f8f58ae25e2a78f31b06edcf26532d634ca554e
- https://github.com/openclaw/openclaw
- https://github.com/openclaw/openclaw/releases/tag/v2026.3.7
