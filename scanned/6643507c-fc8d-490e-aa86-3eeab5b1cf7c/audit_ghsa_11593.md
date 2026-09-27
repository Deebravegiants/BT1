# [M] OpenClaw's Signal reaction-only status events could, in limited cases, be enqueued before access checks

## Summary
Severity: Medium
Advisory: GHSA-792q-qw95-f446
CVE: CVE-2026-32050
CWE: CWE-863
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:H/AT:N/PR:N/UI:N/VC:N/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-03
Source: https://github.com/advisories/GHSA-792q-qw95-f446
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.2.25

## Details
### Summary
In a narrow Signal reaction-notification path, reaction-only inbound events could enqueue a status event before sender access checks were applied.

### Affected Packages / Versions
- Package: `openclaw` (npm)
- Affected: `<= 2026.2.24` (latest published at patch time)
- Fixed: `2026.2.25` 

### Details
In the affected flow (`src/signal/monitor/event-handler.ts`), reaction-only handling could return after `enqueueSystemEvent(...)` before DM/group authorization checks were evaluated for that sender.

This behavior was limited to reaction-only inbound events with reaction notifications enabled. In that case, a sender not authorized for normal DM flow could still queue a Signal reaction status line for that session.

The fix applies shared DM/group access checks before reaction notification enqueue. Pairing behavior for normal DM messages is unchanged.

### Impact
- Limited to Signal reaction-only inbound events.
- Could add an unauthorized reaction status line to agent context for affected sessions.
- Did not directly enable normal DM delivery or direct host command execution.

### Fix Commit(s)
- `2aa7842adeedef423be7ce283a9144b9f1a0a669`

### Release Process Note
`patched_versions` is pre-set to `2026.2.25` so once npm release is out, advisory publish can proceed directly.

OpenClaw thanks @tdjackey for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-792q-qw95-f446
- https://nvd.nist.gov/vuln/detail/CVE-2026-32050
- https://github.com/openclaw/openclaw/commit/2aa7842adeedef423be7ce283a9144b9f1a0a669
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-unauthorized-reaction-status-event-enqueue-via-access-check-bypass
