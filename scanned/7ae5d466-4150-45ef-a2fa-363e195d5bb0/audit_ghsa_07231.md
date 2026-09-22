# [M] Gittensory: Missing contributor-scoped access control on profile endpoint and MCP tool leaks miner financial data

## Summary
Severity: Medium
Advisory: GHSA-382c-vx95-w3p5
CWE: CWE-284
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-07-09
Source: https://github.com/advisories/GHSA-382c-vx95-w3p5
Type: github-advisory

## Affected
- npm: `@jsonbored/gittensory-mcp` — affected >=0

## Details
### Summary
 
`GET /v1/contributors/:login/profile` and the `gittensory_get_contributor_profile` MCP tool skip the contributor-scoped access check that every sibling endpoint enforces. Any authenticated session/API/MCP token holder can read any contributor's profile; for confirmed Gittensor miners that exposes `alphaPerDay`, `taoPerDay`, `usdPerDay` (and the `hotkey` on the REST path). Authenticated cross-contributor disclosure, CWE-284 / IDOR.
 
### Details
 
In `src/api/routes.ts` the profile handler returns `buildContributorProfile(...)` with no `requireContributorAccess` call. Every sibling (`/decision-pack`, `/repos/:owner/:repo/decision`, etc.) gates and 403s on a cross-contributor request — the profile route is the only omission. `buildContributorProfile` (`src/signals/engine.ts`) embeds `hotkey` and the three `*PerDay` fields for any confirmed miner.
 
The MCP tool `getContributorProfile` (`src/mcp/server.ts`) also omits `requireContributorAccess`. Its `redactSensitiveForMcp` filter only strips keys matching `hotkey|coldkey|wallet|private_key|privateKey|mnemonic`, so the hotkey is dropped but `alphaPerDay`/`taoPerDay`/`usdPerDay` pass through.
 
The codebase treats these as secret everywhere else — `decision-pack.ts` destructures the hotkey out before serving, and three sanitizers scrub hotkey/wallet from AI/comment output — which is why this is an oversight, not by-design.
 
Exposure: REST → hotkey + 3 financial fields; MCP → 3 financial fields (hotkey redacted).
 
### PoC
 
1. Get any valid session/API/MCP token.
2. Pick a target `login` that is a confirmed miner.
3. `GET /v1/contributors/{target}/profile` → 200 with `gittensor.hotkey`, `alphaPerDay`, `taoPerDay`, `usdPerDay`.
4. `GET /v1/contributors/{target}/decision-pack` (same token) → 403, proving the missing gate.
5. MCP `gittensory_get_contributor_profile` with `{target}` → result includes the three `*PerDay` fields.
### Impact
 
Any token holder can enumerate other miners' daily TAO/alpha/USD revenue (plus hotkey via REST) without authorization. All miners with snapshot data are affected.

## References
- https://github.com/JSONbored/gittensory/security/advisories/GHSA-382c-vx95-w3p5
- https://github.com/JSONbored/gittensory/commit/811ef5fb9d748170011f8854d88c64627ad666a0
- https://github.com/JSONbored/gittensory
