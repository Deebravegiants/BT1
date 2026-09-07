# [M] OpenClaw: Feishu thread history and quoted messages bypass sender allowlist

## Summary
Severity: Medium
Advisory: GHSA-877v-w3f5-3pcq
CVE: CVE-2026-41406
CWE: CWE-639, CWE-863
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-04-02
Source: https://github.com/advisories/GHSA-877v-w3f5-3pcq
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.3.31

## Details
## Summary
Feishu thread history and quoted messages bypass sender allowlist

## Current Maintainer Triage
- Status: open
- Normalized severity: medium
- Assessment: Real in shipped v2026.3.28 Feishu because fetched quoted/root/thread context bypasses sender allowlists, and SECURITY.md does not exempt remote sender-allowlist bypasses.

## Affected Packages / Versions
- Package: `openclaw` (npm)
- Latest published npm version: `2026.3.31`
- Vulnerable version range: `<=2026.3.28`
- Patched versions: `>= 2026.3.31`
- First stable tag containing the fix: `v2026.3.31`

## Fix Commit(s)
- `f45e5a6569aab1d58cc6de25b19f1dc4c8779b85` — 2026-03-31T19:43:54+09:00

## Release Process Note
- The fix is already present in released version `2026.3.31`.
- This draft looks ready for final maintainer disposition or publication, not additional code-fix work.

OpenClaw thanks @AntAISecurityLab for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-877v-w3f5-3pcq
- https://nvd.nist.gov/vuln/detail/CVE-2026-41406
- https://github.com/openclaw/openclaw/commit/f45e5a6569aab1d58cc6de25b19f1dc4c8779b85
- https://github.com/openclaw/openclaw
- https://github.com/openclaw/openclaw/releases/tag/v2026.3.31
- https://www.vulncheck.com/advisories/openclaw-sender-allowlist-bypass-via-thread-history-and-quoted-messages
