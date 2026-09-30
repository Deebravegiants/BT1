# [M] OpenClaw Twilio voice-call webhook auth bypass when ngrok loopback compatibility is enabled

## Summary
Severity: Medium
Advisory: GHSA-c37p-4qqg-3p76
CVE: CVE-2026-29606
CWE: CWE-306
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:L (CVSS_V3)
Published: 2026-02-18
Source: https://github.com/advisories/GHSA-c37p-4qqg-3p76
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.2.14

## Details
## Summary

A Twilio webhook signature-verification bypass in the voice-call extension could allow unauthenticated webhook requests when a specific ngrok free-tier compatibility option is enabled.

## Impact

This issue is limited to configurations that explicitly enable and expose the voice-call webhook endpoint.

Not affected by default:
- The voice-call extension is optional and disabled by default.
- The bypass only applied when `tunnel.allowNgrokFreeTierLoopbackBypass` was explicitly enabled.
- Exploitation required the webhook to be reachable (typically via a public ngrok URL during development).

Worst case (when exposed and the option was enabled):
- An external attacker could send forged requests to the publicly reachable webhook endpoint that would be accepted without a valid `X-Twilio-Signature`.
- This could result in unauthorized webhook event handling (integrity) and request flooding (availability).

## Affected Packages / Versions

- Package: `openclaw` (npm)
- Affected versions: `<= 2026.2.13` (latest published as of 2026-02-14)
- Patched versions: `>= 2026.2.14` (planned next release; pending publish)

## Fix

`allowNgrokFreeTierLoopbackBypass` no longer bypasses signature verification. It only enables trusting forwarded headers on loopback so the public ngrok URL can be reconstructed for correct signature validation.

Fix commit(s):
- ff11d8793b90c52f8d84dae3fbb99307da51b5c9

Thanks @p80n-sec for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-c37p-4qqg-3p76
- https://nvd.nist.gov/vuln/detail/CVE-2026-29606
- https://github.com/openclaw/openclaw/commit/ff11d8793b90c52f8d84dae3fbb99307da51b5c9
- https://github.com/openclaw/openclaw
- https://github.com/openclaw/openclaw/releases/tag/v2026.2.14
- https://www.vulncheck.com/advisories/openclaw-webhook-signature-verification-bypass-via-ngrok-loopback-compatibility
