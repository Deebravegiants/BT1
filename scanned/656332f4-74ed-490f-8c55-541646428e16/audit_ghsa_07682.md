# [M] OpenClaw's unauthenticated Nostr profile HTTP endpoints allow remote profile/config tampering

## Summary
Severity: Medium
Advisory: GHSA-mv9j-6xhh-g383
CVE: CVE-2026-28450
CWE: CWE-285, CWE-306
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-02-17
Source: https://github.com/advisories/GHSA-mv9j-6xhh-g383
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.2.12

## Details
## Summary
The OpenClaw Nostr channel plugin (optional, disabled by default, installed separately) exposes profile management HTTP endpoints under `/api/channels/nostr/:accountId/profile` (GET/PUT) and `/api/channels/nostr/:accountId/profile/import` (POST). In affected versions, these routes were dispatched via the gateway plugin HTTP layer without requiring gateway authentication, allowing unauthenticated remote callers to read or mutate the Nostr profile and persist changes to the gateway config. Profile updates are also published as a signed Nostr kind:0 event using the bot's private key.

Deployments that do not have the Nostr plugin installed and enabled are not impacted.

## Affected Packages / Versions
- Package: `openclaw` (npm)
- Affected versions: `<= 2026.2.9`
- Fixed versions: `>= 2026.2.12`
- Scope note: only affects deployments with the optional `@openclaw/nostr` plugin installed and enabled

## Details
This is exploitable when the gateway HTTP port is reachable beyond localhost (for example: bound to `0.0.0.0`, exposed on a LAN, behind a reverse proxy, or via Tailscale Funnel/Serve).

Unauthenticated callers could update the Nostr profile and persist the new profile in the gateway config.

## Mitigation
Upgrade to `openclaw` `2026.2.12` or later.

As a temporary mitigation, restrict gateway HTTP exposure (bind loopback-only and/or enforce network-layer access controls) until upgraded.

## Fix
Gateway now requires gateway authentication for plugin HTTP requests under `/api/channels/*` before dispatching to plugin handlers.

Fix commit(s):
- 647d929c9d0fd114249230d939a5cb3b36dc70e7

Thanks @simecek for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-mv9j-6xhh-g383
- https://nvd.nist.gov/vuln/detail/CVE-2026-28450
- https://github.com/openclaw/openclaw/commit/647d929c9d0fd114249230d939a5cb3b36dc70e7
- https://github.com/openclaw/openclaw
- https://github.com/openclaw/openclaw/releases/tag/v2026.2.12
- https://www.vulncheck.com/advisories/openclaw-unauthenticated-profile-tampering-via-nostr-plugin-http-endpoints
