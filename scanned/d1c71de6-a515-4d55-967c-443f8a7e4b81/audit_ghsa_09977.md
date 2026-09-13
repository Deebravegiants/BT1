# [M] OpenClaw: Host exec environment overrides miss proxy, TLS, Docker, and Git TLS controls

## Summary
Severity: Medium
Advisory: GHSA-9gp8-hjxr-6f34
CVE: CVE-2026-41330
CWE: CWE-269, CWE-453
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-04-03
Source: https://github.com/advisories/GHSA-9gp8-hjxr-6f34
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.3.31

## Details
## Summary
Host exec environment overrides miss proxy, TLS, Docker, and Git TLS controls

## Current Maintainer Triage
- Status: open
- Normalized severity: medium
- Assessment: Real in shipped v2026.3.28: host exec env policy still missed proxy, TLS, Docker, and Git TLS variables until 4d912e0451 on 2026-03-31; maintainers already accepted it and the fix is unreleased.

## Affected Packages / Versions
- Package: `openclaw` (npm)
- Latest published npm version: `2026.3.31`
- Vulnerable version range: `<=2026.3.28`
- Patched versions: `>= 2026.3.31`
- First stable tag containing the fix: `v2026.3.31`

## Fix Commit(s)
- `4d912e04519b4bd53b248437c53748cdebce9a41` — 2026-03-31T21:25:36+09:00

OpenClaw thanks @AntAISecurityLab for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-9gp8-hjxr-6f34
- https://nvd.nist.gov/vuln/detail/CVE-2026-41330
- https://github.com/openclaw/openclaw/commit/4d912e04519b4bd53b248437c53748cdebce9a41
- https://github.com/openclaw/openclaw
- https://github.com/openclaw/openclaw/releases/tag/v2026.3.31
- https://www.vulncheck.com/advisories/openclaw-environment-variable-override-via-host-exec-policy
