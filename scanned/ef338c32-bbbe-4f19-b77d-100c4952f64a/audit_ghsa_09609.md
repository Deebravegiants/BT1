# [M] OpenClaw: Browser SSRF policy default allowed private-network navigation

## Summary
Severity: Medium
Advisory: GHSA-53vx-pmqw-863c
CVE: CVE-2026-43527
CWE: CWE-1188, CWE-918
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2026-04-17
Source: https://github.com/advisories/GHSA-53vx-pmqw-863c
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.4.14

## Details
## Summary

Browser SSRF policy default allowed private-network navigation.

## Affected Packages / Versions

- Package: `openclaw`
- Ecosystem: npm
- Affected versions: `< 2026.4.14`
- Patched versions: `>= 2026.4.14`

## Impact

Browser SSRF protection could allow private-network navigation by default in paths where restrictive behavior was expected, exposing internal services or metadata endpoints through browser-driven requests.

## Technical Details

The fix preserves strict SSRF configuration semantics, keeps private-network access disabled unless explicitly opted in, and updates loopback CDP readiness handling for the stricter default.

## Fix

The issue was fixed in #66354 and #66386. The first stable tag containing the fix is `v2026.4.14`, and `openclaw@2026.4.14` includes the fix.

## Fix Commit(s)

- `024f4614a1a1831406e763adc40ef226e3d5e9ed`
- `1dabfef28db523e7de81edeb3dd689e9171236a2`
- `213c36cf51121ef6c05cfccd78037371f968f31a`
- `7eecfa411df3d12e6b810e6ca5df47254fc3db3f`
- PR: #66354, #66386

## Release Process Note

Users should upgrade to `openclaw` 2026.4.14 or newer. The latest npm release, `2026.4.14`, already includes the fix.

## Credits

Thanks to @zsxsoft, with sponsorship from @KeenSecurityLab and @qclawer for reporting this issue.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-53vx-pmqw-863c
- https://nvd.nist.gov/vuln/detail/CVE-2026-43527
- https://github.com/openclaw/openclaw/pull/66354
- https://github.com/openclaw/openclaw/pull/66386
- https://github.com/openclaw/openclaw/commit/024f4614a1a1831406e763adc40ef226e3d5e9ed
- https://github.com/openclaw/openclaw/commit/1dabfef28db523e7de81edeb3dd689e9171236a2
- https://github.com/openclaw/openclaw/commit/213c36cf51121ef6c05cfccd78037371f968f31a
- https://github.com/openclaw/openclaw/commit/7eecfa411df3d12e6b810e6ca5df47254fc3db3f
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-server-side-request-forgery-via-private-network-navigation
