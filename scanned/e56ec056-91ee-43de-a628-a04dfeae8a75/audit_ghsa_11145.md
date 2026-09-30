# [M] OpenClaw: Zalo channel downloads media before sender authorization

## Summary
Severity: Medium
Advisory: GHSA-v2v2-f783-358j
CVE: CVE-2026-33576
CWE: CWE-862, CWE-863
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-03-31
Source: https://github.com/advisories/GHSA-v2v2-f783-358j
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.3.28

## Details
## Summary

The Zalo image path fetched and stored inbound media before the DM/pairing authorization checks ran.

## Impact

Unauthorized senders could force network fetches and disk writes in the inbound media store even when the message itself was rejected.

## Affected Component

`extensions/zalo/src/monitor.ts`

## Fixed Versions

- Affected: `<= 2026.3.24`
- Patched: `>= 2026.3.28`
- Latest stable `2026.3.28` contains the fix.

## Fix

Fixed by commit `68ceaf7a5f` (`zalo: gate image downloads before DM auth`).

OpenClaw thanks @AntAISecurityLab for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-v2v2-f783-358j
- https://nvd.nist.gov/vuln/detail/CVE-2026-33576
- https://github.com/openclaw/openclaw/commit/68ceaf7a5f64a23e78b95eff055e4b497218312a
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-unauthorized-media-download-via-zalo-channel
