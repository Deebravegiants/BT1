# [M] OpenClaw Has a Gateway Control Interface Information Disclosure Vulnerability

## Summary
Severity: Medium
Advisory: GHSA-hr8g-2q7x-3f4w
CVE: CVE-2026-41335
CWE: CWE-200
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:L/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-04-03
Source: https://github.com/advisories/GHSA-hr8g-2q7x-3f4w
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.3.31

## Details
## Summary
OpenClaw Gateway Control Interface Information Disclosure Vulnerability

## Current Maintainer Triage
- Status: narrow
- Normalized severity: low
- Assessment: Released Control UI bootstrap JSON did expose version and assistant agent id, but that is low-severity fingerprinting or info disclosure only; unreleased c5c10adc trims the payload.

## Affected Packages / Versions
- Package: `openclaw` (npm)
- Latest published npm version: `2026.3.31`
- Vulnerable version range: `<=2026.3.28`
- Patched versions: `>= 2026.3.31`
- First stable tag containing the fix: `v2026.3.31`

## Fix Commit(s)
- `c5c10adc022f42eb75ebb3bf364dd607738683b3` — 2026-03-30T15:08:19+01:00

OpenClaw thanks @topsec-bunney for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-hr8g-2q7x-3f4w
- https://nvd.nist.gov/vuln/detail/CVE-2026-41335
- https://github.com/openclaw/openclaw/commit/c5c10adc022f42eb75ebb3bf364dd607738683b3
- https://github.com/openclaw/openclaw
- https://github.com/openclaw/openclaw/releases/tag/v2026.3.31
- https://www.vulncheck.com/advisories/openclaw-information-disclosure-via-control-ui-bootstrap-json
