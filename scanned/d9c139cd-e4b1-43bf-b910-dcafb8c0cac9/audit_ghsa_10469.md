# [M] OpenClaw: Memory dreaming config persistence was reachable from operator.write commands

## Summary
Severity: Medium
Advisory: GHSA-5gjc-grvm-m88j
CVE: CVE-2026-43568
CWE: CWE-266, CWE-863
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N/E:U (CVSS_V4)
Published: 2026-04-17
Source: https://github.com/advisories/GHSA-5gjc-grvm-m88j
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=2026.4.5 <2026.4.10

## Details
## Summary

Memory dreaming config persistence was reachable from operator.write commands.

## Affected Packages / Versions

- Package: `openclaw`
- Ecosystem: npm
- Affected versions: `>= 2026.4.5 < 2026.4.10`
- Patched versions: `>= 2026.4.10`

## Impact

A write-scoped gateway path could toggle persistent memory dreaming settings through `/dreaming`, crossing into an admin-class configuration mutation.

## Technical Details

The fix requires admin scope for persistent dreaming gateway toggles.

## Fix

The issue was fixed in #63872. The first stable tag containing the fix is `v2026.4.10`, and `openclaw@2026.4.14` includes the fix.

## Fix Commit(s)

- `6af17b39e11f5f35e23b7e5a5f71a7d0aa3c7310`
- PR: #63872

## Release Process Note

Users should upgrade to `openclaw` 2026.4.10 or newer. The latest npm release, `2026.4.14`, already includes the fix.

## Credits

Thanks to @zpbrent and @zsxsoft, with sponsorship from @KeenSecurityLab and @qclawer for reporting this issue.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-5gjc-grvm-m88j
- https://github.com/openclaw/openclaw/pull/63872
- https://github.com/openclaw/openclaw/commit/6af17b39e11f5f35e23b7e5a5f71a7d0aa3c7310
- https://github.com/openclaw/openclaw
