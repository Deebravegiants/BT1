# [M] OpenClaw's Synology Chat dmPolicy=allowlist failed open on empty allowedUserIds, allowing unauthorized agent dispatch

## Summary
Severity: Medium
Advisory: GHSA-gw85-xp4q-5gp9
CVE: CVE-2026-31998
CWE: CWE-284, CWE-863
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-03
Source: https://github.com/advisories/GHSA-gw85-xp4q-5gp9
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=2026.2.22 <2026.2.24

## Details
### Summary
In `openclaw` versions `2026.2.22` and `2026.2.23`, the optional `synology-chat` channel plugin had an authorization fail-open condition: when `dmPolicy` was `allowlist` and `allowedUserIds` was empty/unset, unauthorized senders were still allowed through to agent dispatch.

This is assessed as **medium** severity because it requires channel/plugin setup and Synology sender access, but can still trigger downstream agent/tool actions.

### Affected Packages / Versions
- Package: `openclaw` (npm)
- Affected versions: `>= 2026.2.22, <= 2026.2.23`
- Latest published affected version at patch time: `2026.2.23`
- Planned patched version: `2026.2.24`

### Details
Root cause was a policy mismatch across plugin code paths:
1. Default resolved DM policy was `allowlist`.
2. Empty `allowedUserIds` was treated as allow-all.
3. Webhook auth in allowlist mode depended on that helper.

Result: `allowlist` with empty list behaved like open access for inbound Synology senders.

### Fix Commit(s)
- `0ee30361b8f6ef3f110f3a7b001da6dd3df96bb5`
- `7655c0cb3a47d0647cbbf5284e177f90b4b82ddb`

### Release Process Note
`patched_versions` is pre-set to the planned next release (`>= 2026.2.24`). Once npm release `2026.2.24` is published, the advisory can be published directly.

OpenClaw thanks @tdjackey for reporting.


### Publication Update (2026-02-25)
`openclaw@2026.2.24` is published on npm and contains the fix commit(s) listed above. This advisory now marks `>= 2026.2.24` as patched.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-gw85-xp4q-5gp9
- https://nvd.nist.gov/vuln/detail/CVE-2026-31998
- https://github.com/openclaw/openclaw/commit/0ee30361b8f6ef3f110f3a7b001da6dd3df96bb5
- https://github.com/openclaw/openclaw/commit/7655c0cb3a47d0647cbbf5284e177f90b4b82ddb
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-authorization-bypass-in-synology-chat-plugin-via-empty-alloweduserids
