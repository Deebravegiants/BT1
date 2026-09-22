# [M] OpenClaw: Feishu reaction events could bypass group authorization and mention gating

## Summary
Severity: Medium
Advisory: GHSA-m69h-jm2f-2pv8
CWE: CWE-285, CWE-863
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:L/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-13
Source: https://github.com/advisories/GHSA-m69h-jm2f-2pv8
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.3.12

## Details
### Summary

A Feishu reaction-originated synthetic event could misclassify a group conversation as `p2p` when the inbound reaction payload omitted `chat_type`. Authorization and mention-gating logic keyed off that incorrect chat type and evaluated the event as a direct message instead of a group message.

### Impact

This could bypass `groupAllowFrom` and `requireMention` protections for reaction-derived events in Feishu group chats.

### Affected versions

`openclaw` `<= 2026.3.11`

### Patch

Fixed in `openclaw` `2026.3.12`. Reaction events now preserve the correct group context before authorization and mention-gate evaluation. Users should update to `2026.3.12` or later.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-m69h-jm2f-2pv8
- https://github.com/openclaw/openclaw/pull/44088
- https://github.com/openclaw/openclaw/commit/3e730c0332eb0a3dc9e1e8c29a5f95e933317b41
- https://github.com/openclaw/openclaw
- https://github.com/openclaw/openclaw/releases/tag/v2026.3.12
