# [M] OpenClaw: Discord event cover images bypassed sandbox media normalization

## Summary
Severity: Medium
Advisory: GHSA-c9h3-5p7r-mrjh
CVE: CVE-2026-43532
CWE: CWE-184, CWE-22
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2026-04-17
Source: https://github.com/advisories/GHSA-c9h3-5p7r-mrjh
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=2026.4.7 <2026.4.10

## Details
## Summary

Discord event cover images bypassed sandbox media normalization.

## Affected Packages / Versions

- Package: `openclaw`
- Ecosystem: npm
- Affected versions: `>= 2026.4.7 < 2026.4.10`
- Patched versions: `>= 2026.4.10`

## Impact

Discord event cover image parameters could bypass the sandbox media normalization path used for outbound local media, allowing host-local media references to reach a channel action path that expected normalized media.

## Technical Details

The fix includes Discord `eventCreate.image` in sandbox media normalization and adds coverage for the event-create media path.

## Fix

The issue was fixed in #64377. The first stable tag containing the fix is `v2026.4.10`, and `openclaw@2026.4.14` includes the fix.

## Fix Commit(s)

- `979c6f09d6fad96596feb91c905934be7e0b4f15`
- PR: #64377

## Release Process Note

Users should upgrade to `openclaw` 2026.4.10 or newer. The latest npm release, `2026.4.14`, already includes the fix.

## Credits

Thanks to @zsxsoft, with sponsorship from @KeenSecurityLab and @qclawer for reporting this issue.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-c9h3-5p7r-mrjh
- https://nvd.nist.gov/vuln/detail/CVE-2026-43532
- https://github.com/openclaw/openclaw/pull/64377
- https://github.com/openclaw/openclaw/commit/979c6f09d6fad96596feb91c905934be7e0b4f15
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-sandbox-media-normalization-bypass-via-discord-event-cover-image
