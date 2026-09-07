# [M] OpenClaw: Browser snapshot and screenshot routes could expose internal page content after navigation

## Summary
Severity: Medium
Advisory: GHSA-c4qm-58hj-j6pj
CVE: CVE-2026-42436
CWE: CWE-862, CWE-918
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2026-04-17
Source: https://github.com/advisories/GHSA-c4qm-58hj-j6pj
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.4.14

## Details
## Summary

Browser snapshot and screenshot routes could expose internal page content after navigation.

## Affected Packages / Versions

- Package: `openclaw`
- Ecosystem: npm
- Affected versions: `< 2026.4.14`
- Patched versions: `>= 2026.4.14`

## Impact

Authenticated browser tool callers could use snapshot, screenshot, or tab routes that did not consistently validate the final browser target after route-driven navigation. In restrictive browser SSRF configurations this could expose content from internal or otherwise disallowed pages.

## Technical Details

The fix re-checks browser snapshot, screenshot, and tab route results against the configured browser SSRF policy before returning page content. Regression coverage was added around snapshot/screenshot and tab-route flows.

## Fix

The issue was fixed in #66040. The first stable tag containing the fix is `v2026.4.14`, and `openclaw@2026.4.14` includes the fix.

## Fix Commit(s)

- `b75ad800a59009fc47eaa3471410f69046150e59`
- PR: #66040

## Release Process Note

Users should upgrade to `openclaw` 2026.4.14 or newer. The latest npm release, `2026.4.14`, already includes the fix.

## Credits

Thanks to @zsxsoft, with sponsorship from @KeenSecurityLab and @qclawer for reporting this issue.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-c4qm-58hj-j6pj
- https://nvd.nist.gov/vuln/detail/CVE-2026-42436
- https://github.com/openclaw/openclaw/pull/66040
- https://github.com/openclaw/openclaw/commit/b75ad800a59009fc47eaa3471410f69046150e59
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-internal-page-content-exposure-via-browser-snapshot-and-screenshot-routes
