# [M] OpenClaw: Telnyx Webhook Replay Detection Bypass via Base64 Signature Re-encoding

## Summary
Severity: Medium
Advisory: GHSA-37v6-fxx8-xjmx
CVE: CVE-2026-41351
CWE: CWE-294
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-04-03
Source: https://github.com/advisories/GHSA-37v6-fxx8-xjmx
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.3.31

## Details
## Summary
Telnyx Webhook Replay Detection Bypass via Base64 Signature Re-encoding

## Current Maintainer Triage
- Status: narrow
- Normalized severity: low
- Assessment: Shipped v2026.3.28 replay hashing treated equivalent Telnyx Base64/Base64URL signatures as distinct requests, but signature verification still held, so lower to low.

## Affected Packages / Versions
- Package: `openclaw` (npm)
- Latest published npm version: `2026.3.31`
- Vulnerable version range: `<=2026.3.28`
- Patched versions: `>= 2026.3.31`
- First stable tag containing the fix: `v2026.3.31`

## Fix Commit(s)
- `ad77666054651c1fd77b1dc60fd6a8db6600a29a` — 2026-03-30T20:01:43+01:00

## Release Process Note
- The fix is already present in released version `2026.3.31`.
- This draft looks ready for final maintainer disposition or publication, not additional code-fix work.

OpenClaw thanks @AntAISecurityLab for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-37v6-fxx8-xjmx
- https://nvd.nist.gov/vuln/detail/CVE-2026-41351
- https://github.com/openclaw/openclaw/commit/ad77666054651c1fd77b1dc60fd6a8db6600a29a
- https://github.com/openclaw/openclaw
- https://github.com/openclaw/openclaw/releases/tag/v2026.3.31
- https://www.vulncheck.com/advisories/openclaw-webhook-replay-detection-bypass-via-base64-signature-re-encoding
