# [M] OpenClaw: Workspace .env could inject OpenClaw runtime-control variables

## Summary
Severity: Medium
Advisory: GHSA-7wv4-cc7p-jhxc
CVE: CVE-2026-43531
CWE: CWE-15
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-04-17
Source: https://github.com/advisories/GHSA-7wv4-cc7p-jhxc
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.4.9

## Details
## Summary

Workspace .env could inject OpenClaw runtime-control variables.

## Affected Packages / Versions

- Package: `openclaw`
- Ecosystem: npm
- Affected versions: `< 2026.4.9`
- Patched versions: `>= 2026.4.9`

## Impact

A malicious workspace `.env` file could set OpenClaw runtime-control variables affecting update sources, gateway URLs, ClawHub resolution, browser executable paths, and related behavior.

## Technical Details

The fix blocks OpenClaw runtime-control keys and key families from workspace `.env` loading.

## Fix

The issue was fixed in #62660. The first stable tag containing the fix is `v2026.4.9`, and `openclaw@2026.4.14` includes the fix.

## Fix Commit(s)

- `dbfcef319618158fa40b31cdac386ea34c392c0c`
- PR: #62660

## Release Process Note

Users should upgrade to `openclaw` 2026.4.9 or newer. The latest npm release, `2026.4.14`, already includes the fix.

## Credits

Thanks to @zsxsoft, with sponsorship from @KeenSecurityLab for reporting this issue.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-7wv4-cc7p-jhxc
- https://nvd.nist.gov/vuln/detail/CVE-2026-43531
- https://github.com/openclaw/openclaw/pull/62660
- https://github.com/openclaw/openclaw/commit/dbfcef319618158fa40b31cdac386ea34c392c0c
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-environment-variable-injection-via-workspace-env-file
