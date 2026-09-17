# [M] OpenClaw: Feishu card actions could misclassify DMs and skip dmPolicy

## Summary
Severity: Medium
Advisory: GHSA-72q8-jcmc-97wx
CWE: CWE-863
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-04-25
Source: https://github.com/advisories/GHSA-72q8-jcmc-97wx
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.4.20

## Details
## Affected Packages / Versions

- Package: `openclaw` (npm)
- Affected versions: `< 2026.4.20`
- Patched version: `2026.4.20`

## Impact

Feishu card-action callbacks could synthesize a message event with DM conversations classified as group conversations. That skipped `dmPolicy` enforcement for card actions, so a sender in a Feishu DM could trigger card-action flows that should have been blocked by a restrictive DM policy.

The issue is limited to Feishu card-action handling. Severity is medium.

## Fix

OpenClaw now resolves Feishu card-action chat type before dispatch, including API lookup when stored context is unavailable, and avoids falling through to group handling for DMs.

Fix commit:

- `90979d7c3ef7ec30b9f8aa6963a5e38d2f17d166`

## Release

Fixed in OpenClaw `2026.4.20`.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-72q8-jcmc-97wx
- https://github.com/openclaw/openclaw/commit/90979d7c3ef7ec30b9f8aa6963a5e38d2f17d166
- https://github.com/openclaw/openclaw
