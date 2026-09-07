# [M] OpenClaw: iOS A2UI bridge trusted generic local-network pages for agent.request dispatch

## Summary
Severity: Medium
Advisory: GHSA-4p4f-fc8q-84m3
CVE: CVE-2026-41398
CWE: CWE-284
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:L/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-04-07
Source: https://github.com/advisories/GHSA-4p4f-fc8q-84m3
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.4.2

## Details
## Summary
Before OpenClaw 2026.4.2, the iOS A2UI bridge treated generic local-network pages as trusted bridge origins. A page loaded from a local-network or tailnet host could trigger agent.request dispatch without the stricter trusted-canvas origin check.

## Impact
A loaded attacker-controlled page could inject unauthorized non-owner agent.request runs into the active iOS node session, polluting session state and consuming budget. The demonstrated impact did not include owner-only actions or arbitrary host execution.

## Affected Packages / Versions
- Package: openclaw (npm)
- Affected versions: <= 2026.4.1
- Patched versions: >= 2026.4.2
- Latest published npm version: 2026.4.1

## Fix Commit(s)
49d08382a90f71dabe2877b3f6729ad85f808d57 — restrict A2UI action dispatch to trusted canvas URLs

## Release Process Note
The fix is present on main and is staged for OpenClaw 2026.4.2. Publish this advisory after the 2026.4.2 npm release is live.

Thanks [@nexrin](https://github.com/nexrin) for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-4p4f-fc8q-84m3
- https://github.com/openclaw/openclaw/commit/49d08382a90f71dabe2877b3f6729ad85f808d57
- https://github.com/openclaw/openclaw
