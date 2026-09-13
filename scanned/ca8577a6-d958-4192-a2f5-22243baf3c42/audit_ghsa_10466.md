# [H] OpenClaw: busybox and toybox applet execution weakened exec approval binding

## Summary
Severity: High
Advisory: GHSA-2cq5-mf3v-mx44
CVE: CVE-2026-43530
CWE: CWE-863
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-04-17
Source: https://github.com/advisories/GHSA-2cq5-mf3v-mx44
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=2026.2.23 <2026.4.12

## Details
## Summary

busybox and toybox applet execution weakened exec approval binding.

## Affected Packages / Versions

- Package: `openclaw`
- Ecosystem: npm
- Affected versions: `>= 2026.2.23 < 2026.4.12`
- Patched versions: `>= 2026.4.12`

## Impact

Opaque multi-call binaries such as `busybox` and `toybox` could obscure which applet or script-like behavior would actually run, weakening exec approval binding and risk classification.

## Technical Details

The fix treats `busybox` and `toybox` as opaque mutable script runners and fails closed rather than binding unsafe applet invocations.

## Fix

The issue was fixed in #65713. The first stable tag containing the fix is `v2026.4.12`, and `openclaw@2026.4.14` includes the fix.

## Fix Commit(s)

- `666f48d9b882a8a1415ca53f9567c72499d850c9`
- PR: #65713

## Release Process Note

Users should upgrade to `openclaw` 2026.4.12 or newer. The latest npm release, `2026.4.14`, already includes the fix.

## Credits

Thanks to @decsecre583 for reporting this issue.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-2cq5-mf3v-mx44
- https://nvd.nist.gov/vuln/detail/CVE-2026-43530
- https://github.com/openclaw/openclaw/pull/65713
- https://github.com/openclaw/openclaw/commit/666f48d9b882a8a1415ca53f9567c72499d850c9
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-weakened-exec-approval-binding-via-busybox-and-toybox-applet-execution
