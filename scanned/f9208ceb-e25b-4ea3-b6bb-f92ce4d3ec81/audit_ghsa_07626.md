# [H] OpenClaw is Missing Webhook Authentication in Telnyx Provider Allows Unauthenticated Requests

## Summary
Severity: High
Advisory: GHSA-4hg8-92x6-h2f3
CVE: CVE-2026-26319
CWE: CWE-306
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2026-02-17
Source: https://github.com/advisories/GHSA-4hg8-92x6-h2f3
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.2.14

## Details
## Summary

In affected versions, OpenClaw's optional `@openclaw/voice-call` plugin Telnyx webhook handler could accept unsigned inbound webhook requests when `telnyx.publicKey` was not configured, allowing unauthenticated callers to forge Telnyx events.

This only impacts deployments where the Voice Call plugin is installed, enabled, and the webhook endpoint is reachable from the attacker (for example, publicly exposed via a tunnel/proxy).

## Affected Packages / Versions

- Package: `openclaw` (npm)
- Affected: `<= 2026.2.13`
- Fixed: `>= 2026.2.14` (planned)

## Details

Telnyx webhooks are expected to be authenticated via Ed25519 signature verification.

In affected versions, `TelnyxProvider.verifyWebhook()` could effectively fail open when no Telnyx public key was configured, allowing arbitrary HTTP POST requests to the voice-call webhook endpoint to be treated as legitimate Telnyx events.

## Fix

The fix makes Telnyx webhook verification fail closed by default and requires `telnyx.publicKey` (or `TELNYX_PUBLIC_KEY`) to be configured.

A signature verification bypass exists only for local development via `skipSignatureVerification: true`, which is off by default, emits a loud startup warning, and should not be used in production.

This requirement is documented in the Voice Call plugin docs.

## Fix Commit(s)

- `29b587e73cbdc941caec573facd16e87d52f007b`
- `f47584fec` (centralized verification helper + stronger tests)

## Workarounds

- Configure `plugins.entries.voice-call.config.telnyx.publicKey` (or `TELNYX_PUBLIC_KEY`) to enable signature verification.
- Only for local development: set `skipSignatureVerification: true`.

Thanks @p80n-sec for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-4hg8-92x6-h2f3
- https://nvd.nist.gov/vuln/detail/CVE-2026-26319
- https://github.com/openclaw/openclaw/commit/29b587e73cbdc941caec573facd16e87d52f007b
- https://github.com/openclaw/openclaw/commit/f47584fec86d6d73f2d483043a2ad0e7e3c50411
- https://github.com/openclaw/openclaw
- https://github.com/openclaw/openclaw/releases/tag/v2026.2.14
