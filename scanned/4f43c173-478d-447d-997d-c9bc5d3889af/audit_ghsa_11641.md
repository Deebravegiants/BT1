# [H] OpenClaw's dashboard leaked gateway auth material via browser URL/query and localStorage

## Summary
Severity: High
Advisory: GHSA-rchv-x836-w7xp
CWE: CWE-200
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-03-09
Source: https://github.com/advisories/GHSA-rchv-x836-w7xp
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.3.7

## Details
OpenClaw's macOS Dashboard flow exposed Gateway authentication material to browser-controlled surfaces.

Before the fix, the macOS app appended the shared Gateway `token` and `password` to the Dashboard URL query string when opening the Control UI in the browser. The Control UI then imported the token and persisted it into browser `localStorage` under `openclaw.control.settings.v1`.

This expanded exposure of reusable Gateway admin credentials into browser address-bar/query surfaces and persistent script-readable storage.

## Affected Packages / Versions

- Package: `openclaw` (npm)
- Latest published version verified vulnerable: `2026.3.2`
- Affected range: `<= 2026.3.2`
- Patched version: `>= 2026.3.7`

## Impact

An attacker with access to browser-controlled surfaces or persistent browser storage could recover a valid Gateway admin token and reuse it against the OpenClaw management interface.

The exposure chain was:

1. macOS `Open Dashboard` constructed a URL with auth material.
2. The browser received that credential-bearing URL.
3. The Control UI imported the token from the URL.
4. The Control UI persisted the token in `localStorage`.

## Fix

The fix aligns the macOS Dashboard flow with the safer existing CLI/bootstrap pattern and removes persistent browser token storage:

- macOS Dashboard now passes the Gateway token via URL fragment instead of query parameters.
- macOS Dashboard no longer propagates the shared Gateway password into browser URLs.
- Control UI keeps Gateway tokens in memory only for the current tab.
- Control UI scrubs legacy persisted tokens from `openclaw.control.settings.v1` on load.
- Regression tests cover fragment transport, password omission, and token-scrubbing behavior.

## Fix Commit(s)

- `10d0e3f3ca92326df0ca071fabffe463742f263c` (March 7, 2026)

## Release Process Note

npm `2026.3.7` was published on March 8, 2026. This advisory is fixed in the released package.

Thanks @whiter6666 for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-rchv-x836-w7xp
- https://github.com/openclaw/openclaw/commit/10d0e3f3ca92326df0ca071fabffe463742f263c
- https://github.com/openclaw/openclaw
- https://github.com/openclaw/openclaw/releases/tag/v2026.3.7
