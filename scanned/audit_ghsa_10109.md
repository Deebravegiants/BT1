# [M] OpenClaw: Collect-mode queue batches could reuse the last sender authorization context

## Summary
Severity: Medium
Advisory: GHSA-jwrq-8g5x-5fhm
CVE: CVE-2026-43535
CWE: CWE-266, CWE-863
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-04-17
Source: https://github.com/advisories/GHSA-jwrq-8g5x-5fhm
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.4.14

## Details
## Summary

Collect-mode queue batches could reuse the last sender authorization context.

## Affected Packages / Versions

- Package: `openclaw`
- Ecosystem: npm
- Affected versions: `< 2026.4.14`
- Patched versions: `>= 2026.4.14`

## Impact

Collect-mode queued messages from different senders could be drained as one batch using the final sender's authorization context, allowing earlier messages to inherit a more privileged context.

## Technical Details

The fix splits collect-mode batches by sender authorization context before dispatch, preserving each message's own trust state.

## Fix

The issue was fixed in #66024. The first stable tag containing the fix is `v2026.4.14`, and `openclaw@2026.4.14` includes the fix.

## Fix Commit(s)

- `43d4be902755c970b3d15608679761877718da69`
- PR: #66024

## Release Process Note

Users should upgrade to `openclaw` 2026.4.14 or newer. The latest npm release, `2026.4.14`, already includes the fix.

## Credits

Thanks to @zsxsoft, with sponsorship from @KeenSecurityLab and @qclawer for reporting this issue.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-jwrq-8g5x-5fhm
- https://nvd.nist.gov/vuln/detail/CVE-2026-43535
- https://github.com/openclaw/openclaw/pull/66024
- https://github.com/openclaw/openclaw/commit/43d4be902755c970b3d15608679761877718da69
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-authorization-context-reuse-in-collect-mode-queue-batches
