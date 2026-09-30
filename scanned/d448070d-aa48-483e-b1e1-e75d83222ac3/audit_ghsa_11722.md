# [M] OpenClaw is vulnerable to unauthenticated resource exhaustion through its voice call webhook handling

## Summary
Severity: Medium
Advisory: GHSA-rm59-992w-x2mv
CVE: CVE-2026-35626
CWE: CWE-400
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N/E:U (CVSS_V4)
Published: 2026-03-26
Source: https://github.com/advisories/GHSA-rm59-992w-x2mv
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.3.22

## Details
## Summary
Voice Call webhook handling buffered request bodies before provider signature checks, enabling bounded unauthenticated resource exhaustion.

## Affected Packages / Versions
- Package: `openclaw` (npm)
- Affected: < 2026.3.22
- Fixed: >= 2026.3.22
- Latest released tag checked: `v2026.3.23-2` (`630f1479c44f78484dfa21bb407cbe6f171dac87`)
- Latest published npm version checked: `2026.3.23-2`

## Fix Commit(s)
- `651dc7450b68a5396a009db78ef9382633707ead`

## Release Status
The fix shipped in `v2026.3.22` and remains present in `v2026.3.23` and `v2026.3.23-2`.

## Code-Level Confirmation
- extensions/voice-call/src/webhook.ts now enforces header gating and shared pre-auth body caps before reading attacker-controlled request bodies.
- extensions/voice-call/src/webhook.test.ts ships regression coverage for missing-signature, oversize, and timeout pre-auth webhook cases.

OpenClaw thanks @SEORY0 for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-rm59-992w-x2mv
- https://nvd.nist.gov/vuln/detail/CVE-2026-35626
- https://github.com/openclaw/openclaw/commit/630f1479c44f78484dfa21bb407cbe6f171dac87
- https://github.com/openclaw/openclaw/commit/651dc7450b68a5396a009db78ef9382633707ead
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-unauthenticated-resource-exhaustion-via-voice-call-webhook
