# [M] OpenClaw: Shell init-file options could satisfy exec allowlist script matching

## Summary
Severity: Medium
Advisory: GHSA-wpc6-37g7-8q4w
CVE: CVE-2026-41392
CWE: CWE-184
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-04-07
Source: https://github.com/advisories/GHSA-wpc6-37g7-8q4w
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.3.31

## Details
## Summary

Before OpenClaw 2026.3.31, exec allowlist matching could treat shell init-file wrapper invocations as if the approved script itself were being executed. Shell options such as `--rcfile`, `--init-file`, and `--startup-file` could therefore inherit allowlist trust from a matched script path even though the shell loaded attacker-chosen initialization first.

## Impact

This issue only applied when exec allowlist or allow-always behavior was enabled and the attacker could steer a shell-wrapper command shape that used init-file options. The result was a narrower allowlist bypass, not generic arbitrary command execution from an untrusted boundary.

## Affected Packages / Versions

- Package: `openclaw` (npm)
- Affected versions: `< 2026.3.31`
- Patched versions: `>= 2026.3.31`
- Latest published npm version: `2026.4.1`

## Fix Commit(s)

- `0c8375424620e12777ef24c162eedc7e9fcfd7e3` — reject shell init-file script matches

## Release Process Note

The fix shipped in OpenClaw `2026.3.31` on March 31, 2026. The current published npm release `2026.4.1` from April 1, 2026 also contains the fix.

Thanks @cyjhhh for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-wpc6-37g7-8q4w
- https://nvd.nist.gov/vuln/detail/CVE-2026-41392
- https://github.com/openclaw/openclaw/commit/0c8375424620e12777ef24c162eedc7e9fcfd7e3
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-exec-allowlist-bypass-via-shell-init-file-options
