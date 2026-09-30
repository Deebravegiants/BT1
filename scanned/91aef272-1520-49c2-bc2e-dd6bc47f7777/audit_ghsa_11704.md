# [H] OpenClaw: SSRF via Unguarded Configured Base URLs in Multiple Channel Extensions (Incomplete Fix for CVE-2026-28476)

## Summary
Severity: High
Advisory: GHSA-rhfg-j8jq-7v2h
CVE: CVE-2026-35629
CWE: CWE-918
Ecosystem: npm
Published: 2026-03-29
Source: https://github.com/advisories/GHSA-rhfg-j8jq-7v2h
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.3.28

## Details
## Summary

SSRF via Unguarded Configured Base URLs in Multiple Channel Extensions (Incomplete Fix for CVE-2026-28476)

## Affected Packages / Versions

- Package: `openclaw`
- Affected versions: `<= 2026.3.24`
- First patched version: `2026.3.25`
- Latest published npm version at verification time: `2026.3.24`

## Details

Several channel extensions still used raw `fetch()` against configured base URLs without the SSRF guard that was added for CVE-2026-28476. Commit `f92c92515bd439a71bd03eb1bc969c1964f17acf` routes those outbound requests through `fetchWithSsrFGuard` so configured endpoints cannot be rebound to blocked internal destinations.

Verified vulnerable on tag `v2026.3.24` and fixed on `main` by commit `f92c92515bd439a71bd03eb1bc969c1964f17acf`.

## Fix Commit(s)

- `f92c92515bd439a71bd03eb1bc969c1964f17acf`

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-rhfg-j8jq-7v2h
- https://nvd.nist.gov/vuln/detail/CVE-2026-35629
- https://github.com/openclaw/openclaw/commit/f92c92515bd439a71bd03eb1bc969c1964f17acf
- https://github.com/advisories/GHSA-pg2v-8xwh-qhcc
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-server-side-request-forgery-via-unguarded-configured-base-urls-in-channel-extensions
