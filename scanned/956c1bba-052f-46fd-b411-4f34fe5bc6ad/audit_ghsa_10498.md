# [M] OpenClaw: Browser interaction routes could pivot into local CDP and regain file reads

## Summary
Severity: Medium
Advisory: GHSA-qmwg-qprg-3j38
CWE: CWE-693
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:H/AT:N/PR:N/UI:A/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-04-17
Source: https://github.com/advisories/GHSA-qmwg-qprg-3j38
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.4.9

## Details
## Summary

Browser interaction routes could pivot into local CDP and regain file reads.

## Affected Packages / Versions

- Package: `openclaw`
- Ecosystem: npm
- Affected versions: `< 2026.4.9`
- Patched versions: `>= 2026.4.9`

## Impact

Browser act/evaluate interactions could trigger navigation into the local CDP origin and then create or read disallowed `file://` pages despite direct navigation guards.

## Technical Details

The fix re-checks browser URLs after interaction-driven navigations and blocks targets that violate the configured navigation policy.

## Fix

The issue was fixed in #63226. The first stable tag containing the fix is `v2026.4.9`, and `openclaw@2026.4.14` includes the fix.

## Fix Commit(s)

- `5f5b3d733bdd791cb457f838514179e1288b10b3`
- PR: #63226

## Release Process Note

Users should upgrade to `openclaw` 2026.4.9 or newer. The latest npm release, `2026.4.14`, already includes the fix.

## Credits

Thanks to @tdjackey for reporting this issue.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-qmwg-qprg-3j38
- https://github.com/openclaw/openclaw/pull/63226
- https://github.com/openclaw/openclaw/commit/5f5b3d733bdd791cb457f838514179e1288b10b3
- https://github.com/openclaw/openclaw
