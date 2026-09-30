# [H] OpenClaw: Sandbox browser CDP relay could expose DevTools protocol on 0.0.0.0

## Summary
Severity: High
Advisory: GHSA-525j-hqq2-66r4
CWE: CWE-1327, CWE-284
Ecosystem: npm
CVSS: CVSS:4.0/AV:A/AC:L/AT:P/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-04-17
Source: https://github.com/advisories/GHSA-525j-hqq2-66r4
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.4.10

## Details
## Summary

Sandbox browser CDP relay could expose DevTools protocol on 0.0.0.0.

## Affected Packages / Versions

- Package: `openclaw`
- Ecosystem: npm
- Affected versions: `< 2026.4.10`
- Patched versions: `>= 2026.4.10`

## Impact

The sandbox browser CDP relay could bind too broadly, exposing Chrome DevTools Protocol access outside the intended local/sandbox source range.

## Technical Details

The fix enforces CDP source-range restriction by default and avoids broad `0.0.0.0` exposure unless explicitly configured.

## Fix

The issue was fixed in #61404. The first stable tag containing the fix is `v2026.4.10`, and `openclaw@2026.4.14` includes the fix.

## Fix Commit(s)

- `fbf11ebdb7110632f93926d0ac7b48f04cb44d77`
- PR: #61404

## Release Process Note

Users should upgrade to `openclaw` 2026.4.10 or newer. The latest npm release, `2026.4.14`, already includes the fix.

## Credits

Thanks to @zsxsoft, with sponsorship from @KeenSecurityLab and @qclawer for reporting this issue.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-525j-hqq2-66r4
- https://github.com/openclaw/openclaw/pull/61404
- https://github.com/openclaw/openclaw/commit/fbf11ebdb7110632f93926d0ac7b48f04cb44d77
- https://github.com/openclaw/openclaw
