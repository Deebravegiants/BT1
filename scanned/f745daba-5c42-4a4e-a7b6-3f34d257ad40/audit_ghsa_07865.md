# [M] OpenClaw iMessage group allowlist authorization inherited DM pairing-store identities

## Summary
Severity: Medium
Advisory: GHSA-g34w-4xqq-h79m
CVE: CVE-2026-26328
CWE: CWE-284, CWE-863
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2026-02-18
Source: https://github.com/advisories/GHSA-g34w-4xqq-h79m
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.2.14
- npm: `clawdbot` — affected >=0 <2026.2.14

## Details
## Summary
Under iMessage `groupPolicy=allowlist`, group authorization could be satisfied by sender identities coming from the DM pairing store, broadening DM trust into group contexts.

## Details
Affected component: `src/imessage/monitor/monitor-provider.ts`.

Vulnerable logic derived `effectiveGroupAllowFrom` using both the static group allowlist and DM pairing-store identities (`storeAllowFrom`). This allowed a sender approved via DM pairing to satisfy group authorization in groups even if the sender/chat was not explicitly present in `groupAllowFrom`.

This weakens boundary separation between DM pairing and group allowlist authorization.

## Affected Packages / Versions
- `openclaw` (npm): affected `<= 2026.2.13`
- `clawdbot` (npm): affected `<= 2026.1.24-3`

## Fix Commit(s)
- `openclaw/openclaw@872079d42fe105ece2900a1dd6ab321b92da2d59`
- `openclaw/openclaw@90d1e9cd71419168b2faa54a759b124a3eacfae7`

Thanks @vincentkoc for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-g34w-4xqq-h79m
- https://nvd.nist.gov/vuln/detail/CVE-2026-26328
- https://github.com/openclaw/openclaw/commit/872079d42fe105ece2900a1dd6ab321b92da2d59
- https://github.com/openclaw/openclaw
- https://github.com/openclaw/openclaw/releases/tag/v2026.2.14
