# [C] Baileys has message upsert / hist sync spoofing and app state corruption when using maliciously crafted protocolMessage payload

## Summary
Severity: Critical
Advisory: GHSA-qvv5-jq5g-4cgg
CVE: CVE-2026-48063
CWE: CWE-290, CWE-345, CWE-346
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-06-10
Source: https://github.com/advisories/GHSA-qvv5-jq5g-4cgg
Type: github-advisory

## Affected
- npm: `baileys` — affected >=0 <6.7.22
- npm: `@whiskeysockets/baileys` — affected >=0 <6.7.22
- npm: `baileys` — affected >=7.0.0-rc.1 <7.0.0-rc12
- npm: `@whiskeysockets/baileys` — affected >=7.0.0-rc.1 <7.0.0-rc12

## Details
### Impact
Any baileys session under the latest version (< 7.0.0-rc12, and < 6.7.22) can be sent a malicious payload via the placeholderResendMessage and trigger a fake `messages.upsert` event with a **fake message key and payload**. This allows anyone to spoof messages. The same exploit also allows an attacker to corrupt the app state sync system by sending fake key shares, and also allows for history sync spoofing which also serves the same problem, injecting fake previous context or "on-demand" sync.

### Patches
https://github.com/WhiskeySockets/Baileys/commit/3beb08eecfcb4e65722e674034bd84fb11a9de35 This commit has patched the issue, and a version tag has been released under 7.0.0 (6.7.22) for those still on Baileys v6. A new Baileys version, v7.0.0-rc12, has been released to remediate this.


### Workarounds
There are no real workarounds other than dropping `messages.upsert `events that contain a `requestId` field, turning off automatic history sync (`shouldSyncHistoryMessage: () => false`) in socket config. There are no workarounds for the app state sync jamming.

## References
- https://github.com/WhiskeySockets/Baileys/security/advisories/GHSA-qvv5-jq5g-4cgg
- https://github.com/WhiskeySockets/Baileys/commit/3beb08eecfcb4e65722e674034bd84fb11a9de35
- https://github.com/WhiskeySockets/Baileys
