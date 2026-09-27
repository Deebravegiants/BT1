# [H] OpenClaw: config.get redaction bypass through sourceConfig and runtimeConfig aliases

## Summary
Severity: High
Advisory: GHSA-8372-7vhw-cm6q
CVE: CVE-2026-43528
CWE: CWE-212
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-04-17
Source: https://github.com/advisories/GHSA-8372-7vhw-cm6q
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.4.14

## Details
## Summary

config.get redaction bypass through sourceConfig and runtimeConfig aliases.

## Affected Packages / Versions

- Package: `openclaw`
- Ecosystem: npm
- Affected versions: `< 2026.4.14`
- Patched versions: `>= 2026.4.14`

## Impact

An authenticated gateway client with config read access could receive unredacted secrets through alias fields that survived redaction, including provider API keys, gateway auth material, and channel credentials.

## Technical Details

The fix explicitly overwrites `sourceConfig` and `runtimeConfig` with the same redacted copies used for `resolved` and `config`, including the invalid-snapshot branch. Tests now cover both alias fields.

## Fix

The issue was fixed in #66030. The first stable tag containing the fix is `v2026.4.14`, and `openclaw@2026.4.14` includes the fix.

## Fix Commit(s)

- `86734ef93a2f25063371b04f1946eb300548acd4`
- PR: #66030

## Release Process Note

Users should upgrade to `openclaw` 2026.4.14 or newer. The latest npm release, `2026.4.14`, already includes the fix.

## Credits

Thanks to @zsxsoft, with sponsorship from @KeenSecurityLab and @qclawer for reporting this issue.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-8372-7vhw-cm6q
- https://github.com/openclaw/openclaw/pull/66030
- https://github.com/openclaw/openclaw/commit/86734ef93a2f25063371b04f1946eb300548acd4
- https://github.com/openclaw/openclaw
