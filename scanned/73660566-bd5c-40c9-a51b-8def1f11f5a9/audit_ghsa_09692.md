# [H] OpenClaw: Exec environment denylist missed high-risk interpreter startup variables

## Summary
Severity: High
Advisory: GHSA-vfp4-8x56-j7c5
CVE: CVE-2026-43584
CWE: CWE-184
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-04-17
Source: https://github.com/advisories/GHSA-vfp4-8x56-j7c5
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.4.10

## Details
## Summary

Exec environment denylist missed high-risk interpreter startup variables.

## Affected Packages / Versions

- Package: `openclaw`
- Ecosystem: npm
- Affected versions: `< 2026.4.10`
- Patched versions: `>= 2026.4.10`

## Impact

The exec environment policy missed interpreter startup variables such as `VIMINIT`, `EXINIT`, `LUA_INIT`, and `HOSTALIASES`, allowing operator-supplied environment overrides to influence downstream execution or network behavior.

## Technical Details

The fix expands the host environment security policy denylist to cover these and related high-risk environment variables, with regression coverage.

## Fix

The issue was fixed in #63277. The first stable tag containing the fix is `v2026.4.10`, and `openclaw@2026.4.14` includes the fix.

## Fix Commit(s)

- `2d126fc62343a7b6895351f96e4e1474bc358140`
- PR: #63277

## Release Process Note

Users should upgrade to `openclaw` 2026.4.10 or newer. The latest npm release, `2026.4.14`, already includes the fix.

## Credits

Thanks to @feiyang666 of Tencent zhuque Lab (https://github.com/Tencent/AI-Infra-Guard) for reporting this issue.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-vfp4-8x56-j7c5
- https://nvd.nist.gov/vuln/detail/CVE-2026-43584
- https://github.com/openclaw/openclaw/commit/2d126fc62343a7b6895351f96e4e1474bc358140
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-insufficient-environment-variable-denylist-in-exec-policy
