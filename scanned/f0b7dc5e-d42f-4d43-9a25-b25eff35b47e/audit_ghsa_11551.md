# [M] OpenClaw: BlueBubbles Group Reactions Bypass requireMention and Still Enqueue Agent-Visible System Events

## Summary
Severity: Medium
Advisory: GHSA-mw7w-g3mg-xqm7
CWE: CWE-288, CWE-863
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-27
Source: https://github.com/advisories/GHSA-mw7w-g3mg-xqm7
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0

## Details
## Summary

BlueBubbles Group Reactions Bypass requireMention and Still Enqueue Agent-Visible System Events

## Affected Packages / Versions

- Package: `openclaw`
- Affected versions: `<= 2026.3.24`
- First patched version: `2026.3.25`
- Latest published npm version at verification time: `2026.3.24`

## Details

BlueBubbles group reaction events previously bypassed `requireMention` and still enqueued agent-visible system events in groups that were supposed to stay mention-gated. Commit `f8c98630785288cc1f1d0893503ef3b653a3cede` applies the reaction path to the same mention gate as normal group messages.

Verified vulnerable on tag `v2026.3.24` and fixed on `main` by commit `f8c98630785288cc1f1d0893503ef3b653a3cede`.

## Fix Commit(s)

- `f8c98630785288cc1f1d0893503ef3b653a3cede`

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-mw7w-g3mg-xqm7
- https://github.com/openclaw/openclaw/commit/f8c98630785288cc1f1d0893503ef3b653a3cede
- https://github.com/openclaw/openclaw
