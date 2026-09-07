# [H] OpenClaw: OpenShell Mirror Sync — Sandbox Escape via Unrestricted File Sync + Symlink Traversal

## Summary
Severity: High
Advisory: GHSA-cwf8-44x6-32c2
CVE: CVE-2026-41397
CWE: CWE-434, CWE-59
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2026-04-03
Source: https://github.com/advisories/GHSA-cwf8-44x6-32c2
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.3.31

## Details
## Summary
OpenShell Mirror Sync: Sandbox Escape via Unrestricted File Sync + Symlink Traversal

## Current Maintainer Triage
- Status: narrow
- Normalized severity: high
- Assessment: v2026.3.28 still has the mirror-boundary bug because shipped c02ee8 only excluded hooks while unreleased 3b9dab is the first full symlink-free upload and download hardening.

## Affected Packages / Versions
- Package: `openclaw` (npm)
- Latest published npm version: `2026.3.31`
- Vulnerable version range: `<=2026.3.28`
- Patched versions: `>= 2026.3.31`
- First stable tag containing the fix: `v2026.3.31`

## Fix Commit(s)
- `c02ee8a3a4cb390b23afdf21317aa8b2096854d1` — 2026-03-25T19:59:07Z
- `3b9dab0ece4643a9643e6a45459f5c709d3ce320` — 2026-03-30T14:51:44+01:00

OpenClaw thanks @AntAISecurityLab for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-cwf8-44x6-32c2
- https://nvd.nist.gov/vuln/detail/CVE-2026-41397
- https://github.com/openclaw/openclaw/commit/3b9dab0ece4643a9643e6a45459f5c709d3ce320
- https://github.com/openclaw/openclaw/commit/c02ee8a3a4cb390b23afdf21317aa8b2096854d1
- https://github.com/openclaw/openclaw
- https://github.com/openclaw/openclaw/releases/tag/v2026.3.31
- https://www.vulncheck.com/advisories/openclaw-sandbox-escape-via-unrestricted-file-sync-and-symlink-traversal
