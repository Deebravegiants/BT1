# [M] OpenClaw Exposes Credentials Embedded in baseUrl Fields via config.get and channels.status

## Summary
Severity: Medium
Advisory: GHSA-ppwq-6v66-5m6j
CWE: CWE-200, CWE-212, CWE-522
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N/E:U (CVSS_V4)
Published: 2026-03-26
Source: https://github.com/advisories/GHSA-ppwq-6v66-5m6j
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.3.22

## Details
## Summary
Read-scoped gateway snapshots could expose credentials embedded in channel baseUrl and related endpoint fields.

## Affected Packages / Versions
- Package: `openclaw` (npm)
- Affected: < 2026.3.22
- Fixed: >= 2026.3.22
- Latest released tag checked: `v2026.3.23-2` (`630f1479c44f78484dfa21bb407cbe6f171dac87`)
- Latest published npm version checked: `2026.3.23-2`

## Fix Commit(s)
- `f0202264d0de7ad345382b9008c5963bcefb01b7`

## Release Status
The fix shipped in `v2026.3.22` and remains present in `v2026.3.23` and `v2026.3.23-2`.

## Code-Level Confirmation
- src/channels/account-snapshot-fields.ts now strips URL userinfo from channel status snapshot fields.
- src/config/redact-snapshot.ts now redacts credential-bearing baseUrl and httpUrl fields while preserving safe context.

OpenClaw thanks @zpbrent for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-ppwq-6v66-5m6j
- https://github.com/openclaw/openclaw/commit/f0202264d0de7ad345382b9008c5963bcefb01b7
- https://github.com/openclaw/openclaw
