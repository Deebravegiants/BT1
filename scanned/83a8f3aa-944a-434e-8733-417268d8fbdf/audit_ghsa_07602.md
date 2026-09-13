# [H] OpenClaw inter-session prompts could be treated as direct user instructions

## Summary
Severity: High
Advisory: GHSA-w5c7-9qqw-6645
CWE: CWE-345
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:L/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-02-18
Source: https://github.com/advisories/GHSA-w5c7-9qqw-6645
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.2.13

## Details
## Summary

Inter-session messages sent via `sessions_send` could be interpreted as direct end-user instructions because they were persisted as `role: "user"` without provenance metadata.

## Affected Packages / Versions

- Package: `openclaw` (npm)
- Affected versions: `<= 2026.2.12` (i.e. `< 2026.2.13`)
- Fixed in: `2026.2.13` (patched versions `>= 2026.2.13`)

## Impact

A delegated or internal session could inject instructions into another session that appeared equivalent to externally-originated user input.

This is an instruction-provenance confusion issue (confused-deputy style), which can lead to unintended privileged behavior in workflows that trust `role: "user"` as a sole authority signal.

## Technical details

Before the fix, routed inter-session prompts were stored as regular user turns without a verifiable source marker.

As a result, downstream workers and transcript readers could not distinguish:
- External user input
- Internal inter-session routed input

## Fix

OpenClaw now carries explicit input provenance end-to-end for routed prompts.

Key changes:
- Added structured provenance model (`inputProvenance`) with `kind` values including `inter_session`.
- `sessions_send` and agent-to-agent steps now set inter-session provenance when invoking target runs.
- Provenance is persisted on user messages as `message.provenance.kind = "inter_session"` (role remains `user` for provider compatibility).
- Transcript readers and memory helpers were updated to respect provenance and avoid treating inter-session prompts as external user-originated input.
- Runtime context rebuilding now annotates inter-session turns with an explicit in-memory marker (`[Inter-session message]`) for clearer model-side disambiguation.
- Regression tests were added for transcript parsing, session tools flow, runner sanitization, and memory hook behavior.

## Fix Commit(s)

- `85409e401b6586f83954cb53552395d7aab04797`

## Workarounds

If immediate upgrade is not possible:
- Disable or restrict `sessions_send` in affected environments.
- Do not use role alone as an authority boundary; require provenance-aware checks in orchestration logic.

## Credit

Reported by @anbecker.

Thanks @anbecker for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-w5c7-9qqw-6645
- https://github.com/openclaw/openclaw/commit/85409e401b6586f83954cb53552395d7aab04797
- https://github.com/openclaw/openclaw
- https://github.com/openclaw/openclaw/releases/tag/v2026.2.12
