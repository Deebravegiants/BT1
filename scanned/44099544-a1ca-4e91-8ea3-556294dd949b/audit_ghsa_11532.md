# [H] OpenClaw: LINE group allowlist scope mismatch with DM pairing-store entries

## Summary
Severity: High
Advisory: GHSA-gp3q-wpq4-5c5h
CWE: CWE-863
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:H/A:N (CVSS_V3)
Published: 2026-03-12
Source: https://github.com/advisories/GHSA-gp3q-wpq4-5c5h
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.2.26

## Details
### Summary
In specific LINE configurations, sender IDs approved through DM pairing could also satisfy group allowlist checks when operators expected group sender access to be scoped only to explicit group allowlists.

### Affected Packages / Versions
- Package: `openclaw` (npm)
- Latest published version at triage/update time: `2026.2.25`
- Affected: `<= 2026.2.25`
- Patched: `>= 2026.2.26` (planned next release)

### Impact
This is a group-authorization scope mismatch. DM pairing-store entries could influence group sender authorization in allowlist mode.

### Technical Details
Root cause: group allowlist composition inherited pairing-store entries intended for DM approvals. Under default DM pairing policy, a DM-paired sender could match group allowlist checks.

Fixes on `main`:
- isolate group allowlist composition from pairing-store entries
- centralize shared DM/group allowlist composition to preserve DM-only pairing behavior
- add regression coverage for LINE and Mattermost policy paths

### Fix Commit(s)
- `8bdda7a651c21e98faccdbbd73081e79cffe8be0`
- `892a9c24b0f6118729ab5b5f5499b1a7e792dd15` (follow-up refactor hardening)

### Release Process Note
`patched_versions` is pre-set to `>= 2026.2.26` so once npm `2026.2.26` is published, this advisory can be published directly without additional version-field edits.

Thanks @tdjackey for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-gp3q-wpq4-5c5h
- https://github.com/openclaw/openclaw/commit/892a9c24b0f6118729ab5b5f5499b1a7e792dd15
- https://github.com/openclaw/openclaw/commit/8bdda7a651c21e98faccdbbd73081e79cffe8be0
- https://github.com/openclaw/openclaw
