# [C] OpenClaw has an inbound allowlist policy bypass in voice-call extension (empty caller ID + suffix matching)

## Summary
Severity: Critical
Advisory: GHSA-4rj2-gpmh-qq5x
CVE: CVE-2026-28446
CWE: CWE-287
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:L (CVSS_V3)
Published: 2026-02-17
Source: https://github.com/advisories/GHSA-4rj2-gpmh-qq5x
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.2.2

## Details
### Summary

An authentication bypass in the optional `voice-call` extension/plugin allowed unapproved or anonymous callers to reach the voice-call agent when inbound policy was set to `allowlist` or `pairing`.

Deployments that do not install/enable the `voice-call` extension are not affected.

### Affected Packages / Versions

- `openclaw` (npm): `<= 2026.2.1`
- Fixed in: `>= 2026.2.2`

### Details

In affected versions (for example `2026.2.1`), the inbound allowlist check in `extensions/voice-call/src/manager.ts` used suffix-based matching and accepted empty caller IDs after normalization.

This allowed two bypasses:

1. Missing/empty `from` values normalized to an empty string, which caused the allowlist predicate to evaluate as allowed.
2. Suffix-based matching meant any caller number whose digits ended with an allowlisted number would be accepted.

### Proof Of Concept

1. Configure the voice-call extension with `inboundPolicy: allowlist` and `allowFrom: ["+15550001234"]`.
2. Place/trigger an inbound call with missing/empty caller ID (provider-dependent; for example anonymous/restricted caller). The call is accepted.
3. Place a call from a number whose E.164 digits end with `15550001234` (for example `+99915550001234`). The call is accepted.

### Impact

Only operators who install/enable the optional `voice-call` extension and use `inboundPolicy=allowlist` or `pairing` could have inbound access controls bypassed, potentially allowing unauthorized callers to reach auto-response and tool execution.

### Fix

The fix hardens inbound policy handling:

- Reject inbound calls when caller ID is missing.
- Require strict equality when comparing normalized caller IDs against the allowlist (no suffix/prefix matching).
- Add regression tests for missing caller ID, anonymous caller ID, and suffix-collision cases.

Fix commit(s):

- `f8dfd034f5d9235c5485f492a9e4ccc114e97fdb`

Thanks @simecek for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-4rj2-gpmh-qq5x
- https://nvd.nist.gov/vuln/detail/CVE-2026-28446
- https://github.com/openclaw/openclaw/commit/f8dfd034f5d9235c5485f492a9e4ccc114e97fdb
- https://github.com/openclaw/openclaw
- https://github.com/openclaw/openclaw/releases/tag/v2026.2.2
- https://www.vulncheck.com/advisories/openclaw-inbound-allowlist-policy-bypass-in-voice-call-extension-via-empty-caller-id
