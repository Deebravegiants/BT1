# [H] OpenClaw optional voice-call plugin: webhook verification may be bypassed behind certain proxy configurations

## Summary
Severity: High
Advisory: GHSA-3m3q-x3gj-f79x
CVE: CVE-2026-28465
CWE: CWE-287, CWE-290, CWE-345
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2026-02-17
Source: https://github.com/advisories/GHSA-3m3q-x3gj-f79x
Type: github-advisory

## Affected
- npm: `@openclaw/voice-call` — affected >=0 <2026.2.3
- npm: `@clawdbot/voice-call` — affected >=0

## Details
## Affected Packages / Versions

This issue affects the optional voice-call plugin only. It is not enabled by default; it only applies to installations where the plugin is installed and enabled.

- Package: `@openclaw/voice-call`
- Vulnerable versions: `< 2026.2.3`
- Patched versions: `>= 2026.2.3`

Legacy package name (if you are still using it):

- Package: `@clawdbot/voice-call`
- Vulnerable versions: `<= 2026.1.24`
- Patched versions: none published under this package name; migrate to `@openclaw/voice-call`

## Summary

In certain reverse-proxy / forwarding setups, webhook verification can be bypassed if untrusted forwarded headers are accepted.

## Impact

An external party may be able to send voice-call webhook requests that are accepted as valid, which can result in spoofed webhook events being processed.

## Root Cause

Some deployments implicitly trusted forwarded headers (for example `Forwarded` / `X-Forwarded-*`) when determining request properties used during webhook verification. If those headers are not overwritten by a trusted proxy, a client can supply them directly and influence verification.

## Resolution

Ignore forwarded headers by default unless explicitly trusted and allowlisted in configuration. Keep any loopback-only development bypass restricted to local development only. Upgrade to a patched version.

If you cannot upgrade immediately, strip `Forwarded` and `X-Forwarded-*` headers at the edge so clients cannot supply them directly.

## Fix Commit(s)

- `a749db9820eb6d6224032a5a34223d286d2dcc2f`

## Credits

Thanks `@0x5t` for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-3m3q-x3gj-f79x
- https://nvd.nist.gov/vuln/detail/CVE-2026-28465
- https://github.com/openclaw/openclaw/commit/a749db9820eb6d6224032a5a34223d286d2dcc2f
- https://github.com/openclaw/openclaw
- https://github.com/openclaw/openclaw/releases/tag/v2026.2.3
- https://www.vulncheck.com/advisories/openclaw-voice-call-webhook-verification-bypass-via-forwarded-headers
