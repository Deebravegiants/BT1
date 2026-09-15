# [M] OpenClaw: Existing-session browser interaction routes bypassed SSRF policy enforcement

## Summary
Severity: Medium
Advisory: GHSA-527m-976r-jf79
CVE: CVE-2026-43573
CWE: CWE-862, CWE-918
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2026-04-17
Source: https://github.com/advisories/GHSA-527m-976r-jf79
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.4.10

## Details
## Summary

Existing-session browser interaction routes bypassed SSRF policy enforcement.

## Affected Packages / Versions

- Package: `openclaw`
- Ecosystem: npm
- Affected versions: `< 2026.4.10`
- Patched versions: `>= 2026.4.10`

## Impact

Existing-session browser interaction routes could continue interacting with or navigating targets without applying the same SSRF navigation guard used by guarded browser routes.

## Technical Details

The fix guards existing-session navigation and interaction routes with browser navigation policy checks.

## Fix

The issue was fixed in #64370. The first stable tag containing the fix is `v2026.4.10`, and `openclaw@2026.4.14` includes the fix.

## Fix Commit(s)

- `daeb74920d5ad986cb600625180037e23221e93a`
- PR: #64370

## Release Process Note

Users should upgrade to `openclaw` 2026.4.10 or newer. The latest npm release, `2026.4.14`, already includes the fix.

## Credits

Thanks to @zsxsoft, with sponsorship from @KeenSecurityLab and @qclawer for reporting this issue.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-527m-976r-jf79
- https://nvd.nist.gov/vuln/detail/CVE-2026-43573
- https://github.com/openclaw/openclaw/pull/64370
- https://github.com/openclaw/openclaw/commit/daeb74920d5ad986cb600625180037e23221e93a
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-ssrf-policy-bypass-in-existing-session-browser-interaction-routes
