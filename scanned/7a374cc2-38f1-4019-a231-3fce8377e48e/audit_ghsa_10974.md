# [M] OpenClaw: Synology Chat reply delivery could be rebound through username-based user resolution.

## Summary
Severity: Medium
Advisory: GHSA-wv46-v6xc-2qhf
CVE: CVE-2026-35670
CWE: CWE-639, CWE-706, CWE-807
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2026-03-26
Source: https://github.com/advisories/GHSA-wv46-v6xc-2qhf
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.3.22

## Details
## Summary
Synology Chat reply delivery could rebind to a mutable username match instead of the stable numeric user_id recorded by the webhook event.

## Affected Packages / Versions
- Package: `openclaw` (npm)
- Affected: < 2026.3.22
- Fixed: >= 2026.3.22
- Latest released tag checked: `v2026.3.23-2` (`630f1479c44f78484dfa21bb407cbe6f171dac87`)
- Latest published npm version checked: `2026.3.23-2`

## Fix Commit(s)
- `7ade3553b74ee3f461c4acd216653d5ba411f455`

## Release Status
The fix shipped in `v2026.3.22` and remains present in `v2026.3.23` and `v2026.3.23-2`.

## Code-Level Confirmation
- extensions/synology-chat/src/webhook-handler.ts now keeps replies bound to the stable webhook user identifier unless an explicit dangerous opt-in is enabled.
- extensions/synology-chat/src/config-schema.ts contains the explicit dangerous opt-in seam instead of silent username rebinding.

OpenClaw thanks @nexrin for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-wv46-v6xc-2qhf
- https://nvd.nist.gov/vuln/detail/CVE-2026-35670
- https://github.com/openclaw/openclaw/commit/630f1479c44f78484dfa21bb407cbe6f171dac87
- https://github.com/openclaw/openclaw/commit/7ade3553b74ee3f461c4acd216653d5ba411f455
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-webhook-reply-rebinding-via-username-resolution-in-synology-chat
