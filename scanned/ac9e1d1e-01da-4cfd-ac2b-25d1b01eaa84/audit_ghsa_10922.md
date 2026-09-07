# [M] OpenClaw Bypasses DM Policy Separation via Synology Chat Webhook Path Collision 

## Summary
Severity: Medium
Advisory: GHSA-rqp8-q22p-5j9q
CVE: CVE-2026-35635
CWE: CWE-285
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:L/VA:N/SC:L/SI:L/SA:N (CVSS_V4)
Published: 2026-03-26
Source: https://github.com/advisories/GHSA-rqp8-q22p-5j9q
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.3.22

## Details
## Summary
Synology Chat multi-account configuration could collapse onto a shared webhook path, replacing route ownership and bypassing per-account DM policy separation.

## Affected Packages / Versions
- Package: `openclaw` (npm)
- Affected: < 2026.3.22
- Fixed: >= 2026.3.22
- Latest released tag checked: `v2026.3.23-2` (`630f1479c44f78484dfa21bb407cbe6f171dac87`)
- Latest published npm version checked: `2026.3.23-2`

## Fix Commit(s)
- `980940aa58f862da4e19372597bbc2a9f268d70b`

## Release Status
The fix shipped in `v2026.3.22` and remains present in `v2026.3.23` and `v2026.3.23-2`.

## Code-Level Confirmation
- extensions/synology-chat/src/accounts.ts now distinguishes inherited base webhook paths from explicit per-account paths.
- extensions/synology-chat/src/gateway-runtime.ts now fails closed on inherited or duplicate webhook paths and registers routes without replacement.

OpenClaw thanks @tdjackey for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-rqp8-q22p-5j9q
- https://nvd.nist.gov/vuln/detail/CVE-2026-35635
- https://github.com/openclaw/openclaw/commit/630f1479c44f78484dfa21bb407cbe6f171dac87
- https://github.com/openclaw/openclaw/commit/980940aa58f862da4e19372597bbc2a9f268d70b
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-webhook-path-route-replacement-vulnerability-in-synology-chat
