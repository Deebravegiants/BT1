# [H] OpenClaw: Workspace provider auth choices could auto-enable untrusted provider plugins

## Summary
Severity: High
Advisory: GHSA-939r-rj45-g2rj
CVE: CVE-2026-43569
CWE: CWE-829
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-04-17
Source: https://github.com/advisories/GHSA-939r-rj45-g2rj
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.4.9

## Details
## Summary

Workspace provider auth choices could auto-enable untrusted provider plugins.

## Affected Packages / Versions

- Package: `openclaw`
- Ecosystem: npm
- Affected versions: `< 2026.4.9`
- Patched versions: `>= 2026.4.9`

## Impact

Non-interactive onboarding could select a provider auth choice shadowed by an untrusted workspace plugin, auto-enabling that plugin during auth setup.

## Technical Details

The fix prefers trusted provider origins for auth choices and excludes untrusted workspace choices unless they are explicitly enabled.

## Fix

The issue was fixed in #62368. The first stable tag containing the fix is `v2026.4.9`, and `openclaw@2026.4.14` includes the fix.

## Fix Commit(s)

- `2d97eae53e212ae26f3aebcd6a50ffc6877f770d`
- PR: #62368

## Release Process Note

Users should upgrade to `openclaw` 2026.4.9 or newer. The latest npm release, `2026.4.14`, already includes the fix.

## Credits

Thanks to @zpbrent for reporting this issue.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-939r-rj45-g2rj
- https://nvd.nist.gov/vuln/detail/CVE-2026-43569
- https://github.com/openclaw/openclaw/pull/62368
- https://github.com/openclaw/openclaw/commit/2d97eae53e212ae26f3aebcd6a50ffc6877f770d
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-untrusted-provider-plugin-auto-enablement-via-workspace-provider-auth
