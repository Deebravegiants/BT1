# [M] OpenClaw: Slack system events bypass sender authorization in member and message subtype handlers

## Summary
Severity: Medium
Advisory: GHSA-v8cg-4474-49v8
CVE: CVE-2026-32895
CWE: CWE-863
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-03-12
Source: https://github.com/advisories/GHSA-v8cg-4474-49v8
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.2.26

## Details
### Summary
Slack `member_*` and `message` subtype system events (`message_changed`, `message_deleted`, `thread_broadcast`) were not consistently enforcing sender authorization before enqueueing system events.

### Affected Packages / Versions
- Package: `openclaw` (npm)
- Latest published version: `2026.2.25`
- Affected range: `<= 2026.2.25`
- Planned patched version: `2026.2.26` (pre-set for publish-readiness)

### Technical Details
Slack system-event handlers in `src/slack/monitor/events/members.ts` and `src/slack/monitor/events/messages.ts` enqueued events after channel checks without shared sender authorization. Deployments relying on Slack DM allowlists (`dmPolicy` / `allowFrom`) or per-channel `users` allowlists could receive unauthorized system-event ingress from non-allowlisted senders.

The fix routes those handlers through `authorizeAndResolveSlackSystemEventContext(...)` and fails closed when message subtype sender identity cannot be resolved.

### Fix Commit(s)
- `3d30ba18a2aba1e1b302e77ff33145c3b06c01c8`

### Release Process Note
`patched_versions` is pre-set to `>= 2026.2.26` so once npm `2026.2.26` is published, this advisory can be published without further field edits.

Thanks @tdjackey for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-v8cg-4474-49v8
- https://nvd.nist.gov/vuln/detail/CVE-2026-32895
- https://github.com/openclaw/openclaw/commit/3d30ba18a2aba1e1b302e77ff33145c3b06c01c8
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-sender-authorization-bypass-in-slack-system-event-handlers
