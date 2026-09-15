# [H] OpenClaw: Matrix profile config persistence was reachable from operator.write message tools

## Summary
Severity: High
Advisory: GHSA-7jp6-r74r-995q
CVE: CVE-2026-42433
CWE: CWE-266, CWE-862, CWE-863
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2026-04-17
Source: https://github.com/advisories/GHSA-7jp6-r74r-995q
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.4.10

## Details
## Summary

Matrix profile config persistence was reachable from operator.write message tools.

## Affected Packages / Versions

- Package: `openclaw`
- Ecosystem: npm
- Affected versions: `< 2026.4.10`
- Patched versions: `>= 2026.4.10`

## Impact

Gateway `operator.write` message-tool paths could reach Matrix profile persistence that should have required admin-level authority.

## Technical Details

The fix gates Matrix profile updates for non-owner message-tool runs and prevents write-scoped callers from mutating persistent profile config.

## Fix

The issue was fixed in #62662. The first stable tag containing the fix is `v2026.4.10`, and `openclaw@2026.4.14` includes the fix.

## Fix Commit(s)

- `fe0f686c9228fffcec6de4011da45e69a6e23e54`
- PR: #62662

## Release Process Note

Users should upgrade to `openclaw` 2026.4.10 or newer. The latest npm release, `2026.4.14`, already includes the fix.

## Credits

Thanks to @zpbrent and @zsxsoft, with sponsorship from @KeenSecurityLab and @qclawer for reporting this issue.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-7jp6-r74r-995q
- https://nvd.nist.gov/vuln/detail/CVE-2026-42433
- https://github.com/openclaw/openclaw/pull/62662
- https://github.com/openclaw/openclaw/commit/fe0f686c9228fffcec6de4011da45e69a6e23e54
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-unauthorized-matrix-profile-config-persistence-access-via-operator-write-message-tools
