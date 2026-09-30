# [H] OpenClaw: PIP_INDEX_URL and UV_INDEX_URL bypass host exec env sanitization and redirect Python package-index traffic

## Summary
Severity: High
Advisory: GHSA-7ggg-pvrf-458v
CVE: CVE-2026-41391
CWE: CWE-184, CWE-807
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:L/I:H/A:N (CVSS_V3)
Published: 2026-04-02
Source: https://github.com/advisories/GHSA-7ggg-pvrf-458v
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.3.31

## Details
## Summary
`PIP_INDEX_URL` and `UV_INDEX_URL` bypass host exec env sanitization and redirect Python package-index traffic

## Current Maintainer Triage
- Status: narrow
- Normalized severity: high
- Assessment: v2026.3.28 still allows Python package-index env redirection through host exec, but scope should stay limited to approved or allowlisted package-management exec paths, not arbitrary remote execution.

## Affected Packages / Versions
- Package: `openclaw` (npm)
- Latest published npm version: `2026.3.31`
- Vulnerable version range: `<=2026.3.28`
- Patched versions: `>= 2026.3.31`
- First stable tag containing the fix: `v2026.3.31`

## Fix Commit(s)
- `7ae1bb0c7799fd0cbd2d4de7b0f5b8039837ab8d` — 2026-03-31T09:53:32+09:00

OpenClaw thanks @nexrin for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-7ggg-pvrf-458v
- https://nvd.nist.gov/vuln/detail/CVE-2026-41391
- https://github.com/openclaw/openclaw/commit/7ae1bb0c7799fd0cbd2d4de7b0f5b8039837ab8d
- https://github.com/openclaw/openclaw
- https://github.com/openclaw/openclaw/releases/tag/v2026.3.31
- https://www.vulncheck.com/advisories/openclaw-environment-variable-bypass-in-package-index-url-handling
