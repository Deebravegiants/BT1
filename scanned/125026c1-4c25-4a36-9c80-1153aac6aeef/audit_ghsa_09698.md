# [M] OpenClaw: QQBot reply media URL handling could trigger SSRF and re-upload fetched bytes

## Summary
Severity: Medium
Advisory: GHSA-2767-2q9v-9326
CVE: CVE-2026-43526
CWE: CWE-918
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2026-04-17
Source: https://github.com/advisories/GHSA-2767-2q9v-9326
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.4.12

## Details
## Summary

QQBot reply media URL handling could trigger SSRF and re-upload fetched bytes.

## Affected Packages / Versions

- Package: `openclaw`
- Ecosystem: npm
- Affected versions: `< 2026.4.12`
- Patched versions: `>= 2026.4.12`

## Impact

QQBot reply media URLs could be treated as trusted media sources, allowing SSRF fetches whose returned bytes were then re-uploaded through the channel.

## Technical Details

The fix routes QQBot remote media fetches through SSRF-guarded media fetching and explicit URL allowlist policy.

## Fix

The issue was fixed in #63495 and #65788. The first stable tag containing the fix is `v2026.4.12`, and `openclaw@2026.4.14` includes the fix.

## Fix Commit(s)

- `08ae021d1f4f02e0ca5fd8a3b9659291c1ecf95a`
- `ddb7a8dd80b8d5dd04aafa44ce7a4354b568bb2d`
- PR: #63495, #65788

## Release Process Note

Users should upgrade to `openclaw` 2026.4.12 or newer. The latest npm release, `2026.4.14`, already includes the fix.

## Credits

Thanks to @threalwinky for reporting this issue.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-2767-2q9v-9326
- https://nvd.nist.gov/vuln/detail/CVE-2026-43526
- https://github.com/openclaw/openclaw/pull/63495
- https://github.com/openclaw/openclaw/pull/65788
- https://github.com/openclaw/openclaw/commit/08ae021d1f42905a85a550813c0d95169b171a6c
- https://github.com/openclaw/openclaw/commit/08ae021d1f4f02e0ca5fd8a3b9659291c1ecf95a
- https://github.com/openclaw/openclaw/commit/ddb7a8dd80b8d5dd04aafa44ce7a4354b568bb2d
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-server-side-request-forgery-via-qqbot-reply-media-url-handling
