# [H] OpenClaw: SSH sandbox tar upload follows symlinks, enabling arbitrary file write on remote host

## Summary
Severity: High
Advisory: GHSA-fv94-qvg8-xqpw
CVE: CVE-2026-41364
CWE: CWE-59, CWE-61
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:H (CVSS_V3)
Published: 2026-04-02
Source: https://github.com/advisories/GHSA-fv94-qvg8-xqpw
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.3.31

## Details
## Summary
SSH sandbox tar upload follows symlinks, enabling arbitrary file write on remote host

## Current Maintainer Triage
- Status: open
- Normalized severity: high
- Assessment: Real in shipped v2026.3.28: SSH sandbox tar upload lacked pre-upload symlink escape rejection until 3d5af14984 on 2026-03-31; maintainers already accepted it and the fix is unreleased.

## Affected Packages / Versions
- Package: `openclaw` (npm)
- Latest published npm version: `2026.3.31`
- Vulnerable version range: `<=2026.3.28`
- Patched versions: `>= 2026.3.31`
- First stable tag containing the fix: `v2026.3.31`

## Fix Commit(s)
- `3d5af14984ac1976c747a8e11581d697bd0829dc` — 2026-03-31T19:56:45+09:00

OpenClaw thanks @AntAISecurityLab for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-fv94-qvg8-xqpw
- https://nvd.nist.gov/vuln/detail/CVE-2026-41364
- https://github.com/openclaw/openclaw/commit/3d5af14984ac1976c747a8e11581d697bd0829dc
- https://github.com/openclaw/openclaw
- https://github.com/openclaw/openclaw/releases/tag/v2026.3.31
- https://www.vulncheck.com/advisories/openclaw-arbitrary-file-write-via-symlink-following-in-ssh-sandbox-tar-upload
