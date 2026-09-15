# [M] OpenClaw: Shell-wrapper detection missed env-argv assignment injection forms

## Summary
Severity: Medium
Advisory: GHSA-j6c7-3h5x-99g9
CVE: CVE-2026-42435
CWE: CWE-78
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:H/AT:N/PR:N/UI:N/VC:N/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-04-17
Source: https://github.com/advisories/GHSA-j6c7-3h5x-99g9
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=2026.2.22 <2026.4.12

## Details
## Summary

Shell-wrapper detection missed env-argv assignment injection forms.

## Affected Packages / Versions

- Package: `openclaw`
- Ecosystem: npm
- Affected versions: `>= 2026.2.22 < 2026.4.12`
- Patched versions: `>= 2026.4.12`

## Impact

Exec preflight handling missed shell-wrapper and argv-level environment assignment forms that could affect execution semantics, including high-risk shell environment controls.

## Technical Details

The fix broadens shell-wrapper detection and blocks environment assignments in argv forms. High-risk shell variables such as `SHELLOPTS` and `PS4` are covered by the host environment security policy.

## Fix

The issue was fixed in #65717. The first stable tag containing the fix is `v2026.4.12`, and `openclaw@2026.4.14` includes the fix.

## Fix Commit(s)

- `8f8492d172f4c5b4fd7dd9a47855ed620c8770ab`
- PR: #65717

## Release Process Note

Users should upgrade to `openclaw` 2026.4.12 or newer. The latest npm release, `2026.4.14`, already includes the fix.

## Credits

Thanks to @decsecre583 for reporting this issue.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-j6c7-3h5x-99g9
- https://github.com/openclaw/openclaw/pull/65717
- https://github.com/openclaw/openclaw/commit/8f8492d172f4c5b4fd7dd9a47855ed620c8770ab
- https://github.com/openclaw/openclaw
