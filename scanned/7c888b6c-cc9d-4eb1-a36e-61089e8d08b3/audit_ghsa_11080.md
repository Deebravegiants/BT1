# [M] OpenClaw's voice-call Twilio webhook replay could bypass manager dedupe because normalized event IDs were randomized per parse

## Summary
Severity: Medium
Advisory: GHSA-vqx8-9xxw-f2m7
CVE: CVE-2026-32053
CWE: CWE-294, CWE-863
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:L/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-03
Source: https://github.com/advisories/GHSA-vqx8-9xxw-f2m7
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.2.23

## Details
## Impact
Twilio webhook replay events could bypass voice-call manager dedupe because normalized event IDs were randomized per parse. A replayed event could be treated as new and trigger duplicate or stale call-state transitions.

## Affected Packages / Versions
- Package: `openclaw` (npm)
- Vulnerable versions: `<= 2026.2.22-2`
- Patched version (released): `>= 2026.2.23`

## Remediation
The fix preserves provider event IDs through normalization, adds bounded replay dedupe in webhook security validation, and enforces per-call turn-token checks on call-state transitions.

## Fix Commit(s)
- 1d28da55a5d0ff409e34999e0961157e9db0a2ab

## Release Process Note
`patched_versions` is pre-set to the released version (`2026.2.23`) This advisory now reflects released fix version `2026.2.23`.2.23`.

OpenClaw thanks @jiseoung for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-vqx8-9xxw-f2m7
- https://nvd.nist.gov/vuln/detail/CVE-2026-32053
- https://github.com/openclaw/openclaw/commit/1d28da55a5d0ff409e34999e0961157e9db0a2ab
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-twilio-webhook-replay-bypass-via-randomized-event-id-normalization
