# [H] OpenClaw: QQBot media tags could read arbitrary local files through reply text

## Summary
Severity: High
Advisory: GHSA-66r7-m7xm-v49h
CVE: CVE-2026-43533
CWE: CWE-22
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-04-17
Source: https://github.com/advisories/GHSA-66r7-m7xm-v49h
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.4.10

## Details
## Summary

QQBot media tags could read arbitrary local files through reply text.

## Affected Packages / Versions

- Package: `openclaw`
- Ecosystem: npm
- Affected versions: `< 2026.4.10`
- Patched versions: `>= 2026.4.10`

## Impact

QQBot outbound media tags in AI reply text could reference host-local paths outside the intended media storage boundary, allowing local file disclosure through outbound media handling.

## Technical Details

The fix enforces the media storage boundary for all outbound QQBot local file paths.

## Fix

The issue was fixed in #63271. The first stable tag containing the fix is `v2026.4.10`, and `openclaw@2026.4.14` includes the fix.

## Fix Commit(s)

- `604777e4414cc3b2ff8861f18f4fb04374c702c6`
- PR: #63271

## Release Process Note

Users should upgrade to `openclaw` 2026.4.10 or newer. The latest npm release, `2026.4.14`, already includes the fix.

## Credits

Thanks to @feiyang666 of Tencent zhuque Lab (https://github.com/Tencent/AI-Infra-Guard) for reporting this issue.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-66r7-m7xm-v49h
- https://github.com/openclaw/openclaw/pull/63271
- https://github.com/openclaw/openclaw/commit/604777e4414cc3b2ff8861f18f4fb04374c702c6
- https://github.com/openclaw/openclaw
