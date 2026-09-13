# [M] OpenClaw: Heartbeat owner downgrade missed local async exec completion events

## Summary
Severity: Medium
Advisory: GHSA-g375-h3v6-4873
CWE: CWE-269
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-04-17
Source: https://github.com/advisories/GHSA-g375-h3v6-4873
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=2026.3.31 <2026.4.10

## Details
## Summary

Heartbeat owner downgrade missed local async exec completion events.

## Affected Packages / Versions

- Package: `openclaw`
- Ecosystem: npm
- Affected versions: `>= 2026.3.31 < 2026.4.10`
- Patched versions: `>= 2026.4.10`

## Impact

Local background exec completion text could be missed by heartbeat owner-downgrade detection, leaving a run in a more privileged context than intended after untrusted completion content.

## Technical Details

The fix expands exec-completion detection to local background exec formats and adds targeted tests.

## Fix

The issue was fixed in #64376. The first stable tag containing the fix is `v2026.4.10`, and `openclaw@2026.4.14` includes the fix.

## Fix Commit(s)

- `19a2e9ddb5a8a494abcba812bb11f51075026a27`
- PR: #64376

## Release Process Note

Users should upgrade to `openclaw` 2026.4.10 or newer. The latest npm release, `2026.4.14`, already includes the fix.

## Credits

Thanks to @zsxsoft, with sponsorship from @KeenSecurityLab and @qclawer for reporting this issue.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-g375-h3v6-4873
- https://github.com/openclaw/openclaw/pull/64376
- https://github.com/openclaw/openclaw/commit/19a2e9ddb5a8a494abcba812bb11f51075026a27
- https://github.com/openclaw/openclaw
