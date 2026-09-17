# [M] OpenClaw: Browser press/type interaction routes missed complete navigation guard coverage

## Summary
Severity: Medium
Advisory: GHSA-536q-mj95-h29h
CVE: CVE-2026-43580
CWE: CWE-862, CWE-918
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2026-04-17
Source: https://github.com/advisories/GHSA-536q-mj95-h29h
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.4.10

## Details
## Summary

Browser press/type interaction routes missed complete navigation guard coverage.

## Affected Packages / Versions

- Package: `openclaw`
- Ecosystem: npm
- Affected versions: `< 2026.4.10`
- Patched versions: `>= 2026.4.10`

## Impact

Some browser press/type style interactions could trigger navigation without complete post-action SSRF policy enforcement.

## Technical Details

The fix applies a three-phase interaction navigation guard to navigation-capable interactions, including pressKey and type submit flows.

## Fix

The issue was fixed in #62023 and #63226 and #63889. The first stable tag containing the fix is `v2026.4.10`, and `openclaw@2026.4.14` includes the fix.

## Fix Commit(s)

- `049acf23cb03e1b92f5c71cd99c6ec5f35cc56fe`
- `5f5b3d733bdd791cb457f838514179e1288b10b3`
- `e0b8ddc1a55185aff1cf9e0e095014d2e4f1d894`
- PR: #62023, #63226, #63889

## Release Process Note

Users should upgrade to `openclaw` 2026.4.10 or newer. The latest npm release, `2026.4.14`, already includes the fix.

## Credits

Thanks to @zsxsoft, with sponsorship from @KeenSecurityLab and @qclawer for reporting this issue.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-536q-mj95-h29h
- https://nvd.nist.gov/vuln/detail/CVE-2026-43580
- https://github.com/openclaw/openclaw/pull/62023
- https://github.com/openclaw/openclaw/pull/63226
- https://github.com/openclaw/openclaw/pull/63889
- https://github.com/openclaw/openclaw/commit/049acf23cb03e1b92f5c71cd99c6ec5f35cc56fe
- https://github.com/openclaw/openclaw/commit/5f5b3d733bdd791cb457f838514179e1288b10b3
- https://github.com/openclaw/openclaw/commit/e0b8ddc1a55185aff1cf9e0e095014d2e4f1d894
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-incomplete-navigation-guard-coverage-in-browser-interactions
