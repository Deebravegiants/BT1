# [M] OpenClaw's MS Teams sender allowlist bypass when route allowlist is configured and sender allowlist is empty

## Summary
Severity: Medium
Advisory: GHSA-g7cr-9h7q-4qxq
CVE: CVE-2026-34506
CWE: CWE-289
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-12
Source: https://github.com/advisories/GHSA-g7cr-9h7q-4qxq
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.3.8

## Details
OpenClaw's Microsoft Teams plugin widened group sender authorization when a team/channel route allowlist was configured but `groupAllowFrom` was empty. Before the fix, a matching route allowlist entry could cause the message handler to synthesize wildcard sender authorization for that route, allowing any sender in the matched team/channel to bypass the intended `groupPolicy: "allowlist"` sender check.

This does not affect default unauthenticated access, but it does weaken a documented Teams group authorization boundary and can allow unauthorized group senders to trigger replies in allowlisted Teams routes.

## Affected Packages / Versions

- Package: `openclaw` (npm)
- Latest published vulnerable version: `2026.3.7`
- Affected range: `<= 2026.3.7`
- Fixed in released version: `2026.3.8`

## Fix Commit(s)

- `88aee9161e0e6d32e810a25711e32a808a1777b2`

## Release Verification

- Verified fixed in GitHub release `v2026.3.8` published on March 9, 2026.
- Verified `npm view openclaw version` resolves to `2026.3.8`.
- Verified the release contains the regression test covering the Teams route-allowlist sender-bypass case and that the test passes against the `v2026.3.8` tree.

Thanks @zpbrent for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-g7cr-9h7q-4qxq
- https://nvd.nist.gov/vuln/detail/CVE-2026-34506
- https://github.com/openclaw/openclaw/commit/88aee9161e0e6d32e810a25711e32a808a1777b2
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-sender-allowlist-bypass-in-microsoft-teams-plugin-via-route-allowlist-configuration
