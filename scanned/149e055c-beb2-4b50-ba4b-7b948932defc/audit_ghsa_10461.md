# [H] OpenClaw: Voice-call realtime WebSocket accepted oversized frames

## Summary
Severity: High
Advisory: GHSA-vw3h-q6xq-jjm5
CVE: CVE-2026-42437
CWE: CWE-400, CWE-770
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-04-17
Source: https://github.com/advisories/GHSA-vw3h-q6xq-jjm5
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=2026.4.9 <2026.4.10

## Details
## Summary

Voice-call realtime WebSocket accepted oversized frames.

## Affected Packages / Versions

- Package: `openclaw`
- Ecosystem: npm
- Affected versions: `>= 2026.4.9 < 2026.4.10`
- Patched versions: `>= 2026.4.10`

## Impact

The voice-call realtime WebSocket path could accept oversized frames, creating a remote availability risk for deployments exposing that webhook path.

## Technical Details

The fix rejects oversized realtime WebSocket frames before processing them.

## Fix

The issue was fixed in #63890. The first stable tag containing the fix is `v2026.4.10`, and `openclaw@2026.4.14` includes the fix.

## Fix Commit(s)

- `afadb7dae6738819ad9c7d2597ace0516957d20e`
- PR: #63890

## Release Process Note

Users should upgrade to `openclaw` 2026.4.10 or newer. The latest npm release, `2026.4.14`, already includes the fix.

## Reporters

Thanks to G0odUser from ADLab of VenusTech
Thanks to @zsxsoft, with sponsorship from @KeenSecurityLab and @qclawer for reporting this issue.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-vw3h-q6xq-jjm5
- https://nvd.nist.gov/vuln/detail/CVE-2026-42437
- https://github.com/openclaw/openclaw/pull/63890
- https://github.com/openclaw/openclaw/commit/afadb7dae6738819ad9c7d2597ace0516957d20e
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-denial-of-service-via-oversized-websocket-frames-in-voice-call-realtime-path
