# [M] OpenClaw: Sandbox noVNC helper route exposed interactive browser session credentials

## Summary
Severity: Medium
Advisory: GHSA-92jp-89mq-4374
CWE: CWE-306
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:L/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-04-17
Source: https://github.com/advisories/GHSA-92jp-89mq-4374
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=2026.2.21 <2026.4.10

## Details
## Summary

Sandbox noVNC helper route exposed interactive browser session credentials.

## Affected Packages / Versions

- Package: `openclaw`
- Ecosystem: npm
- Affected versions: `>= 2026.2.21 < 2026.4.10`
- Patched versions: `>= 2026.4.10`

## Impact

The sandbox noVNC helper route could be reached without the intended bridge authentication, exposing an interactive browser session surface.

## Technical Details

The fix gates the sandbox noVNC helper route behind bridge authentication.

## Fix

The issue was fixed in #63882. The first stable tag containing the fix is `v2026.4.10`, and `openclaw@2026.4.14` includes the fix.

## Fix Commit(s)

- `8dfbf3268bd224b7377d1ecca77a445100746085`
- PR: #63882

## Release Process Note

Users should upgrade to `openclaw` 2026.4.10 or newer. The latest npm release, `2026.4.14`, already includes the fix.

## Credits

Thanks to @zsxsoft, with sponsorship from @KeenSecurityLab and @qclawer for reporting this issue.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-92jp-89mq-4374
- https://github.com/openclaw/openclaw/pull/63882
- https://github.com/openclaw/openclaw/commit/8dfbf3268bd224b7377d1ecca77a445100746085
- https://github.com/openclaw/openclaw
