# [M] OpenClaw: LINE webhook handler lacks shared pre-auth concurrency budget before signature verification

## Summary
Severity: Medium
Advisory: GHSA-qcc3-jqwp-5vh2
CVE: CVE-2026-41343
CWE: CWE-770, CWE-799
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2026-04-02
Source: https://github.com/advisories/GHSA-qcc3-jqwp-5vh2
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.3.31

## Details
## Summary
LINE webhook handler lacks shared pre-auth concurrency budget before signature verification

## Current Maintainer Triage
- Status: open
- Normalized severity: low
- Assessment: Shipped v2026.3.28 lacks a shared pre-auth concurrency budget on the public LINE webhook path, but the effect is bounded transient availability loss only, so low fits.

## Affected Packages / Versions
- Package: `openclaw` (npm)
- Latest published npm version: `2026.3.31`
- Vulnerable version range: `<=2026.3.28`
- Patched versions: `>= 2026.3.31`
- First stable tag containing the fix: `v2026.3.31`

## Fix Commit(s)
- `57c47d8c7fbf5a2e70cc4dec2380977968903cad` — 2026-03-31T19:34:25+09:00

OpenClaw thanks @nexrin for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-qcc3-jqwp-5vh2
- https://nvd.nist.gov/vuln/detail/CVE-2026-41343
- https://github.com/openclaw/openclaw/commit/57c47d8c7fbf5a2e70cc4dec2380977968903cad
- https://github.com/openclaw/openclaw
- https://github.com/openclaw/openclaw/releases/tag/v2026.3.31
- https://www.vulncheck.com/advisories/openclaw-denial-of-service-via-line-webhook-handler-pre-auth-concurrency
