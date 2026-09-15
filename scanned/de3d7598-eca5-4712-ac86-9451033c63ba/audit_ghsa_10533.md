# [M] OpenClaw: screen_record outPath bypassed workspace-only filesystem guard

## Summary
Severity: Medium
Advisory: GHSA-jf25-7968-h2h5
CVE: CVE-2026-43567
CWE: CWE-22, CWE-863
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:N/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-04-17
Source: https://github.com/advisories/GHSA-jf25-7968-h2h5
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.4.10

## Details
## Summary

screen_record outPath bypassed workspace-only filesystem guard.

## Affected Packages / Versions

- Package: `openclaw`
- Ecosystem: npm
- Affected versions: `< 2026.4.10`
- Patched versions: `>= 2026.4.10`

## Impact

The node-host screen recording tool could honor an `outPath` outside the workspace guard, allowing an authorized tool call to write outside the intended workspace boundary.

## Technical Details

The fix applies the workspace-root guard to node tool `outPath` handling, including screen recording paths.

## Fix

The issue was fixed in #63551. The first stable tag containing the fix is `v2026.4.10`, and `openclaw@2026.4.14` includes the fix.

## Fix Commit(s)

- `635bb35b68d8faa5bfa2fda35feadd315122748a`
- PR: #63551

## Release Process Note

Users should upgrade to `openclaw` 2026.4.10 or newer. The latest npm release, `2026.4.14`, already includes the fix.

## Credits

Thanks to @anshumanbh for reporting this issue.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-jf25-7968-h2h5
- https://github.com/openclaw/openclaw/pull/63551
- https://github.com/openclaw/openclaw/commit/635bb35b68d8faa5bfa2fda35feadd315122748a
- https://github.com/openclaw/openclaw
