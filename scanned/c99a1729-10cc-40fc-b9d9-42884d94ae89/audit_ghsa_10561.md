# [M] OpenClaw: Unauthenticated plugin-auth HTTP routes receive operator runtime scopes

## Summary
Severity: Medium
Advisory: GHSA-mhgq-xpfq-6r66
CVE: CVE-2026-41394
CWE: CWE-269, CWE-862
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:H/A:N (CVSS_V3)
Published: 2026-04-02
Source: https://github.com/advisories/GHSA-mhgq-xpfq-6r66
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.3.31

## Details
## Summary
Unauthenticated plugin-auth HTTP routes receive operator runtime scopes

## Current Maintainer Triage
- Status: narrow
- Normalized severity: medium
- Assessment: v2026.3.28 still gives auth:"plugin" routes operator WRITE_SCOPE, but impact should stay limited to plugin routes that actually touch privileged runtime actions before plugin auth completes.

## Affected Packages / Versions
- Package: `openclaw` (npm)
- Latest published npm version: `2026.3.31`
- Vulnerable version range: `<=2026.3.28`
- Patched versions: `>= 2026.3.31`
- First stable tag containing the fix: `v2026.3.31`

## Fix Commit(s)
- `2a1db0c0f1fa375004a95ba0ef030534790a6d47` — 2026-04-01T00:20:49+09:00

OpenClaw thanks @davidluzsilva for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-mhgq-xpfq-6r66
- https://nvd.nist.gov/vuln/detail/CVE-2026-41394
- https://github.com/openclaw/openclaw/commit/2a1db0c0f1fa375004a95ba0ef030534790a6d47
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-unauthorized-operator-scope-access-in-unauthenticated-plugin-auth-routes
