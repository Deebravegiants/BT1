# [H] OpenClaw has a webhook auth bypass when gateway is behind a reverse proxy (loopback remoteAddress trust)

## Summary
Severity: High
Advisory: GHSA-xc7w-v5x6-cc87
CVE: CVE-2026-29613
CWE: CWE-306
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2026-02-17
Source: https://github.com/advisories/GHSA-xc7w-v5x6-cc87
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.2.12

## Details
## Summary

The BlueBubbles webhook handler previously treated any request whose socket `remoteAddress` was loopback (`127.0.0.1`, `::1`, `::ffff:127.0.0.1`) as authenticated. When OpenClaw Gateway is behind a reverse proxy (Tailscale Serve/Funnel, nginx, Cloudflare Tunnel, ngrok), the proxy typically connects to the gateway over loopback, allowing unauthenticated remote requests to bypass the configured webhook password.

This could allow an attacker who can reach the proxy endpoint to inject arbitrary inbound BlueBubbles message/reaction events.

## Affected Packages / Versions

- Package: `openclaw` (npm)
- Affected versions: `< 2026.2.12`
- Patched versions: `>= 2026.2.12`

## Exposure / Configuration

- BlueBubbles is an optional channel plugin (intended to eventually replace the legacy iMessage plugin, which is also optional). It is not enabled by default and is not part of a standard OpenClaw configuration.
- Only deployments with the BlueBubbles webhook endpoint exposed through a reverse proxy are impacted.

## Details

The BlueBubbles webhook handler accepts inbound events via an HTTP POST endpoint under the configured BlueBubbles webhook path.

In vulnerable versions, the handler would accept requests as authenticated if `req.socket.remoteAddress` is loopback, without validating forwarding headers. With common reverse-proxy setups, the gateway sees the proxy as the direct client (loopback), even when the original request is remote.

## Fix

- Primary fix (released in `2026.2.12`): remove loopback-based authentication bypass and require the configured webhook secret.
- Defense-in-depth follow-up (next release after commit below): treat requests with forwarding headers as proxied and never accept passwordless webhooks through a proxy.

## Fix Commit(s)

- [`f836c385ffc746cb954e8ee409f99d079bfdcd2f`](https://github.com/openclaw/openclaw/commit/f836c385ffc746cb954e8ee409f99d079bfdcd2f) (released in `2026.2.12`)
- [`743f4b28495cdeb0d5bf76f6ebf4af01f6a02e5a`](https://github.com/openclaw/openclaw/commit/743f4b28495cdeb0d5bf76f6ebf4af01f6a02e5a) (defense-in-depth follow-up)

## Mitigations

- Ensure a BlueBubbles webhook password is configured.
- Do not expose the gateway webhook endpoint publicly without authentication.

Thanks @simecek for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-xc7w-v5x6-cc87
- https://nvd.nist.gov/vuln/detail/CVE-2026-29613
- https://github.com/openclaw/openclaw/commit/743f4b28495cdeb0d5bf76f6ebf4af01f6a02e5a
- https://github.com/openclaw/openclaw/commit/f836c385ffc746cb954e8ee409f99d079bfdcd2f
- https://github.com/openclaw/openclaw
- https://github.com/openclaw/openclaw/releases/tag/v2026.2.12
- https://www.vulncheck.com/advisories/openclaw-webhook-authentication-bypass-via-loopback-remoteaddress-trust
