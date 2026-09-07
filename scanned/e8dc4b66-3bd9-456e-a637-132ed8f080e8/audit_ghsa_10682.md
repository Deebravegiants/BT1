# [M] OpenClaw: Owner-enforced commands could accept wildcard channel senders as command owners

## Summary
Severity: Medium
Advisory: GHSA-c28g-vh7m-fm7v
CVE: CVE-2026-44991
CWE: CWE-862
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-04-29
Source: https://github.com/advisories/GHSA-c28g-vh7m-fm7v
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.4.21

## Details
## Impact

OpenClaw deployments before `2026.4.21` could treat a non-owner sender as authorized for owner-enforced slash commands when all of the following were true:

- a channel plugin declared `commands.enforceOwnerForCommands: true`;
- the channel accepted wildcard inbound senders with `allowFrom: ["*"]`;
- no explicit `commands.ownerAllowFrom` was configured.

In that state, `src/auto-reply/command-auth.ts` reused the channel inbound wildcard as part of the command-owner decision. A sender who was not the owner could therefore pass the owner-command gate for commands such as `/send`, `/config`, or `/debug` on the affected channel.

The issue is limited to the command-owner authorization axis. It does not by itself grant owner-only tool access, host/sandbox access, or gateway administrator scope.

## Affected Packages / Versions

- Package: `openclaw` on npm
- Affected versions: `<= 2026.4.20`
- Patched version: `2026.4.21`

The latest public release, `2026.4.21`, contains the fix.

## Patches

The fix requires a concrete owner identity or internal operator-admin scope when a plugin enforces owner-only commands. Wildcard channel `allowFrom` no longer implies wildcard command ownership.

Fix commits:

- `2aa93d44a1b2c7058c371f261fda2b5d4de4a882` on `main`
- `995febb7b1e811ff6a1df5b18c22de94103f4c9f` in the `2026.4.21` release line

## Workarounds

Upgrade to `openclaw@2026.4.21` or later. Before upgrading, avoid wildcard/open-DM sender policy on owner-enforced channels, or configure `commands.ownerAllowFrom` to the intended owner identities.

## Credits

OpenClaw thanks @zsxsoft for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-c28g-vh7m-fm7v
- https://nvd.nist.gov/vuln/detail/CVE-2026-44991
- https://github.com/openclaw/openclaw/commit/2aa93d44a1b2c7058c371f261fda2b5d4de4a882
- https://github.com/openclaw/openclaw/commit/995febb7b1e811ff6a1df5b18c22de94103f4c9f
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-authorization-bypass-in-owner-enforced-commands-via-wildcard-channel-senders
