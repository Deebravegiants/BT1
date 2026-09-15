# [M] OpenClaw: Voice-call Plivo replay mutates in-process callback origin before replay rejection

## Summary
Severity: Medium
Advisory: GHSA-89r3-6x4j-v7wf
CVE: CVE-2026-41337
CWE: CWE-294
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-04-02
Source: https://github.com/advisories/GHSA-89r3-6x4j-v7wf
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.3.31

## Details
## Summary
Voice-call Plivo replay mutates in-process callback origin before replay rejection

## Current Maintainer Triage
- Status: narrow
- Normalized severity: low
- Assessment: v2026.3.28 can still mutate Plivo callback origin before replay rejection, but this needs a captured valid callback for a live call so medium is overstated.

## Affected Packages / Versions
- Package: `openclaw` (npm)
- Latest published npm version: `2026.3.31`
- Vulnerable version range: `<=2026.3.28`
- Patched versions: `>= 2026.3.31`
- First stable tag containing the fix: `v2026.3.31`

## Fix Commit(s)
- `efe9183f9d2fd5e01c8068fa01f4a07a58a63c0b` — 2026-03-31T19:50:35+09:00

## Release Process Note
- The fix is already present in released version `2026.3.31`.
- This draft looks ready for final maintainer disposition or publication, not additional code-fix work.

Thanks @zsxsoft for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-89r3-6x4j-v7wf
- https://nvd.nist.gov/vuln/detail/CVE-2026-41337
- https://github.com/openclaw/openclaw/commit/efe9183f9d2fd5e01c8068fa01f4a07a58a63c0b
- https://github.com/openclaw/openclaw
- https://github.com/openclaw/openclaw/releases/tag/v2026.3.31
- https://www.vulncheck.com/advisories/openclaw-callback-origin-mutation-in-plivo-voice-call-replay
