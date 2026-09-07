# [M] OpenClaw: Forged Nostr DMs could create pairing state before signature verification

## Summary
Severity: Medium
Advisory: GHSA-h43v-27wg-5mf9
CVE: CVE-2026-41301
CWE: CWE-347
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2026-04-07
Source: https://github.com/advisories/GHSA-h43v-27wg-5mf9
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=2026.3.22 <2026.3.31

## Details
## Summary

Before OpenClaw 2026.3.31, the Nostr DM ingress path could issue pairing challenges before validating the event signature. A forged DM could create a pending pairing entry and trigger a pairing-reply attempt before signature rejection.

## Impact

An unauthenticated remote sender could consume shared pairing capacity and trigger bounded relay/logging work on the Nostr channel. This issue did not grant message decryption, pairing approval, or broader authorization bypass.

## Affected Packages / Versions

- Package: `openclaw` (npm)
- Affected versions: `>= 2026.3.22, < 2026.3.31`
- Patched versions: `>= 2026.3.31`
- Latest published npm version: `2026.4.1`

## Fix Commit(s)

- `4ee742174f36b5445703e3b1ef2fbd6ae6700fa4` — verify inbound DM signatures before pairing replies

## Release Process Note

The fix shipped in OpenClaw `2026.3.31` on March 31, 2026. The current published npm release `2026.4.1` from April 1, 2026 also contains the fix.

Thanks @smaeljaish771 for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-h43v-27wg-5mf9
- https://nvd.nist.gov/vuln/detail/CVE-2026-41301
- https://github.com/openclaw/openclaw/commit/4ee742174f36b5445703e3b1ef2fbd6ae6700fa4
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-forged-nostr-dm-pairing-state-creation-via-signature-verification-bypass
