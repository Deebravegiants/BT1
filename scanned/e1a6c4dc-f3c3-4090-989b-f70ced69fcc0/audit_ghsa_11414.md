# [H] OpenClaw: Discord text `/approve` bypasses `channels.discord.execApprovals.approvers` and allows non-approvers to resolve pending exec approvals

## Summary
Severity: High
Advisory: GHSA-98hh-7ghg-x6rq
CVE: CVE-2026-41303
CWE: CWE-863
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-03-31
Source: https://github.com/advisories/GHSA-98hh-7ghg-x6rq
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.3.28

## Details
## Summary

Discord text approval commands resolved pending exec approvals without honoring the configured approver allowlist.

## Impact

A Discord user who was allowed to send commands but was not in the approver list could still approve pending host execution.

## Affected Component

`extensions/discord/src/exec-approvals.ts, src/auto-reply/reply/commands-approve.ts`

## Fixed Versions

- Affected: `<= 2026.3.24`
- Patched: `>= 2026.3.28`
- Latest stable `2026.3.28` contains the fix.

## Fix

Fixed by commit `355abe5eba` (`Discord: enforce approver checks for text approvals`).

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-98hh-7ghg-x6rq
- https://nvd.nist.gov/vuln/detail/CVE-2026-41303
- https://github.com/openclaw/openclaw/commit/355abe5eba28012e6a95b9923a32831fcf870344
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-authorization-bypass-in-discord-text-approval-commands
