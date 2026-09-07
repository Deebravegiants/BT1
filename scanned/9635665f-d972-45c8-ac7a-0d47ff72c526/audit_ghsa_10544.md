# [M] OpenClaw: SSRF via Unguarded `fetch()` in Marketplace Plugin Download and Ollama Model Discovery

## Summary
Severity: Medium
Advisory: GHSA-9q7v-8mr7-g23p
CVE: CVE-2026-41302
CWE: CWE-918
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2026-04-02
Source: https://github.com/advisories/GHSA-9q7v-8mr7-g23p
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.3.31

## Details
## Summary
SSRF via Unguarded `fetch()` in Marketplace Plugin Download and Ollama Model Discovery

## Current Maintainer Triage
- Status: narrow
- Normalized severity: medium
- Assessment: Keep the shipped marketplace archive-fetch SSRF, but narrow out the Ollama half because it is operator-configured and overlaps weaker trust-model or duplicate SSRF ground.

## Affected Packages / Versions
- Package: `openclaw` (npm)
- Latest published npm version: `2026.3.31`
- Vulnerable version range: `<=2026.3.28`
- Patched versions: `>= 2026.3.31`
- First stable tag containing the fix: `v2026.3.31`

## Fix Commit(s)
- `8deb9522f3d2680820588b190adb4a2a52f3670b` — 2026-03-30T20:08:38+01:00

OpenClaw thanks @tdjackey for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-9q7v-8mr7-g23p
- https://nvd.nist.gov/vuln/detail/CVE-2026-41302
- https://github.com/openclaw/openclaw/commit/8deb9522f3d2680820588b190adb4a2a52f3670b
- https://github.com/openclaw/openclaw
- https://github.com/openclaw/openclaw/releases/tag/v2026.3.31
- https://www.vulncheck.com/advisories/openclaw-server-side-request-forgery-via-unguarded-fetch-in-marketplace-plugin-download
