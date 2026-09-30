# [H] OpenClaw: Nostr inbound DMs could trigger unauthenticated crypto work before sender policy enforcement

## Summary
Severity: High
Advisory: GHSA-65h8-27jh-q8wv
CVE: CVE-2026-35627
CWE: CWE-863
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-26
Source: https://github.com/advisories/GHSA-65h8-27jh-q8wv
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.3.22

## Details
## Summary
Nostr inbound DM handling could perform crypto and dispatch work before sender and pairing policy enforcement, enabling unauthorized pre-auth computation.

## Affected Packages / Versions
- Package: `openclaw` (npm)
- Affected: < 2026.3.22
- Fixed: >= 2026.3.22
- Latest released tag checked: `v2026.3.23-2` (`630f1479c44f78484dfa21bb407cbe6f171dac87`)
- Latest published npm version checked: `2026.3.23-2`

## Fix Commit(s)
- `1ee9611079e81b9122f4bed01abb3d9f56206c77`

## Release Status
The fix shipped in `v2026.3.22` and remains present in `v2026.3.23` and `v2026.3.23-2`.

## Code-Level Confirmation
- extensions/nostr/src/channel.ts now performs authorization before decrypting and dispatching inbound DM content.
- extensions/nostr/src/nostr-bus.ts adds pre-crypto authorization, size, and rate guardrails before expensive decrypt work.

OpenClaw thanks @kuranikaran for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-65h8-27jh-q8wv
- https://nvd.nist.gov/vuln/detail/CVE-2026-35627
- https://github.com/openclaw/openclaw/commit/1ee9611079e81b9122f4bed01abb3d9f56206c77
- https://github.com/openclaw/openclaw/commit/630f1479c44f78484dfa21bb407cbe6f171dac87
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-unauthenticated-cryptographic-work-in-nostr-inbound-dm-handling
