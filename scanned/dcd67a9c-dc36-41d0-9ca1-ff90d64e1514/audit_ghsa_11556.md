# [M] OpenClaw's Slack reaction/pin sender-policy consistency issue in non-message ingress

## Summary
Severity: Medium
Advisory: GHSA-rm2p-j3r7-4x4j
CVE: CVE-2026-32899
CWE: CWE-863
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2026-03-03
Source: https://github.com/advisories/GHSA-rm2p-j3r7-4x4j
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.2.25

## Details
### Summary
OpenClaw Slack monitor handled `reaction_*` and `pin_*` non-message events before applying sender-policy checks consistently.

In affected versions, these events could be added to system-event context even when sender policy would not normally allow them.

### Affected Packages / Versions
- Package: npm `openclaw`
- Latest published affected version confirmed: `2026.2.24` (npm latest as of February 26, 2026)
- Affected range: `<= 2026.2.24`
- Patched version : `2026.2.25`

### Technical Details
- `reaction_*` and `pin_*` handlers now route through shared sender authorization (`authorizeSlackSystemEventSender`).
- Enforced checks now include:
  - DM `dmPolicy` / `allowFrom`
  - channel `users` allowlist enforcement for non-DM channels
  - channel-level allow checks before system-event enqueue
- Regression coverage added for DM allow/deny and channel-user allowlist deny paths.

### Fix Commit(s)
- `aedf62ac7e669a89c7b299201bf6537dc6b12e0e`
- `75dfb71e4e8b7c2feba5a8ca662f92ea840e0147`

### Impact
Low-severity policy-consistency issue in Slack non-message event ingress.
This may introduce unexpected reaction/pin context signals from senders outside configured policy.

### Release Process Note
`patched_versions` is pre-set to planned release `2026.2.25`. Advisory published with npm release `2026.2.25`.

OpenClaw thanks @tdjackey for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-rm2p-j3r7-4x4j
- https://nvd.nist.gov/vuln/detail/CVE-2026-32899
- https://github.com/openclaw/openclaw/commit/75dfb71e4e8b7c2feba5a8ca662f92ea840e0147
- https://github.com/openclaw/openclaw/commit/aedf62ac7e669a89c7b299201bf6537dc6b12e0e
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-sender-policy-bypass-in-slack-reaction-and-pin-event-handlers
