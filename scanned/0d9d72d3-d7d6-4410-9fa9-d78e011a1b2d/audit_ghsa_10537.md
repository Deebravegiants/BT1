# [H] OpenClaw: Channel setup catalog lookups could include untrusted workspace plugin shadows

## Summary
Severity: High
Advisory: GHSA-82qx-6vj7-p8m2
CVE: CVE-2026-43571
CWE: CWE-829, CWE-862
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-04-17
Source: https://github.com/advisories/GHSA-82qx-6vj7-p8m2
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.4.10

## Details
## Summary

Channel setup catalog lookups could include untrusted workspace plugin shadows.

## Affected Packages / Versions

- Package: `openclaw`
- Ecosystem: npm
- Affected versions: `< 2026.4.10`
- Patched versions: `>= 2026.4.10`

## Impact

Channel setup could resolve a workspace plugin shadow before a bundled channel plugin, causing setup-time plugin loading without the intended trust gate.

## Technical Details

The fix routes setup catalog lookups through trusted catalog paths and uses `excludeWorkspace: true` where setup should not include workspace shadows.

## Fix

The issue was fixed in the advisory fix branch. The first stable tag containing the fix is `v2026.4.10`, and `openclaw@2026.4.14` includes the fix.

## Fix Commit(s)

- `1fede43b948df40ca8674511d4bd08d39f6c5837`
- PR: private advisory fork

## Release Process Note

Users should upgrade to `openclaw` 2026.4.10 or newer. The latest npm release, `2026.4.14`, already includes the fix.

## Credits

Thanks to @zsxsoft, with sponsorship from @KeenSecurityLab and @qclawer for reporting this issue.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-82qx-6vj7-p8m2
- https://nvd.nist.gov/vuln/detail/CVE-2026-43571
- https://github.com/openclaw/openclaw/commit/1fede43b948df40ca8674511d4bd08d39f6c5837
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-untrusted-workspace-plugin-shadow-resolution-in-channel-setup
