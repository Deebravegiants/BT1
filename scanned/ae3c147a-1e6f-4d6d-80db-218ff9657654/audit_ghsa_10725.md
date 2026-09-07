# [M] OpenClaw: Browser SSRF hostname validation could be bypassed by DNS rebinding

## Summary
Severity: Medium
Advisory: GHSA-xq94-r468-qwgj
CVE: CVE-2026-43582
CWE: CWE-350, CWE-918
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2026-04-17
Source: https://github.com/advisories/GHSA-xq94-r468-qwgj
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.4.10

## Details
## Summary

Browser SSRF hostname validation could be bypassed by DNS rebinding.

## Affected Packages / Versions

- Package: `openclaw`
- Ecosystem: npm
- Affected versions: `< 2026.4.10`
- Patched versions: `>= 2026.4.10`

## Impact

Browser navigation policy could validate a hostname/IP resolution that differed from the address Chromium ultimately used, allowing DNS rebinding style SSRF pivots.

## Technical Details

The fix tightens strict browser hostname navigation so unallowlisted hostname URLs fail closed under restrictive policy.

## Fix

The issue was fixed in #64367. The first stable tag containing the fix is `v2026.4.10`, and `openclaw@2026.4.14` includes the fix.

## Fix Commit(s)

- `121c452d666d4749744dc2089287d0227aae2ed3`
- PR: #64367

## Release Process Note

Users should upgrade to `openclaw` 2026.4.10 or newer. The latest npm release, `2026.4.14`, already includes the fix.

## Credits

Thanks to @zsxsoft, with sponsorship from @KeenSecurityLab and @qclawer for reporting this issue.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-xq94-r468-qwgj
- https://nvd.nist.gov/vuln/detail/CVE-2026-43582
- https://github.com/openclaw/openclaw/pull/64367
- https://github.com/openclaw/openclaw/commit/121c452d666d4749744dc2089287d0227aae2ed3
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-dns-rebinding-ssrf-via-hostname-validation-bypass
