# [M] OpenClaw Nostr privateKey config redaction bypass leaks plaintext signing key via config.get

## Summary
Severity: Medium
Advisory: GHSA-jjw7-3vjf-fg5j
CVE: CVE-2026-41385
CWE: CWE-200, CWE-312
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-04-02
Source: https://github.com/advisories/GHSA-jjw7-3vjf-fg5j
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.3.31

## Details
## Summary
OpenClaw Nostr privateKey config redaction bypass leaks plaintext signing key via config.get

## Current Maintainer Triage
- Status: open
- Normalized severity: medium
- Assessment: v2026.3.28 still models Nostr privateKey as plain string so config views can expose it, and the secret-schema fix is unreleased.

## Affected Packages / Versions
- Package: `openclaw` (npm)
- Latest published npm version: `2026.3.31`
- Vulnerable version range: `<=2026.3.28`
- Patched versions: `>= 2026.3.31`
- First stable tag containing the fix: `v2026.3.31`

## Fix Commit(s)
- `57700d716f660591fb6e09727f3ca8041fa48b9d` — 2026-03-31T19:55:03+09:00

## Release Process Note
- The fix is already present in released version `2026.3.31`.
- This draft looks ready for final maintainer disposition or publication, not additional code-fix work.

Thanks @ccreater222 for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-jjw7-3vjf-fg5j
- https://nvd.nist.gov/vuln/detail/CVE-2026-41385
- https://github.com/openclaw/openclaw/commit/57700d716f660591fb6e09727f3ca8041fa48b9d
- https://github.com/openclaw/openclaw
- https://github.com/openclaw/openclaw/releases/tag/v2026.3.31
- https://www.vulncheck.com/advisories/openclaw-nostr-private-key-exposure-via-config-get-redaction-bypass
