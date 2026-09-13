# [M] OpenClaw: Nostr profile mutation routes allowed operator.write config persistence

## Summary
Severity: Medium
Advisory: GHSA-f3h5-h452-vp3j
CWE: CWE-266, CWE-863
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-04-17
Source: https://github.com/advisories/GHSA-f3h5-h452-vp3j
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.4.10

## Details
## Summary

Nostr profile mutation routes allowed operator.write config persistence.

## Affected Packages / Versions

- Package: `openclaw`
- Ecosystem: npm
- Affected versions: `< 2026.4.10`
- Patched versions: `>= 2026.4.10`

## Impact

Nostr plugin HTTP profile routes could persist profile config through a path that did not require admin authority.

## Technical Details

The fix requires `operator.admin` scope for Nostr profile mutation routes.

## Fix

The issue was fixed in #63553. The first stable tag containing the fix is `v2026.4.10`, and `openclaw@2026.4.14` includes the fix.

## Fix Commit(s)

- `6517c700de9bb0ee11b41ab625ef3b63d01b6083`
- PR: #63553

## Release Process Note

Users should upgrade to `openclaw` 2026.4.10 or newer. The latest npm release, `2026.4.14`, already includes the fix.

## Credits

Thanks to @zpbrent and @zsxsoft, with sponsorship from @KeenSecurityLab and @qclawer for reporting this issue.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-f3h5-h452-vp3j
- https://github.com/openclaw/openclaw/pull/63553
- https://github.com/openclaw/openclaw
