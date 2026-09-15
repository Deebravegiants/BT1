# [H] Caddy Defender trusted proxy client IP bypass

## Summary
Severity: High
Advisory: GHSA-3h23-rrpc-3p87
CVE: CVE-2026-46415
CWE: CWE-284, CWE-348
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2026-05-19
Source: https://github.com/advisories/GHSA-3h23-rrpc-3p87
Type: github-advisory

## Affected
- Go: `pkg.jsn.cam/caddy-defender` — affected >=0 <0.10.1

## Details
### Impact

Caddy Defender used `r.RemoteAddr` when evaluating whether a request should be blocked. `RemoteAddr` is the address of the immediate peer connected to Caddy.

In deployments where Caddy is behind a trusted proxy, CDN, or load balancer, the immediate peer is usually the proxy, not the original client. Caddy resolves the original client address into its `client_ip` request variable after applying the configured `trusted_proxies` policy, but Defender did not use that value.

As a result, clients from blocked IP ranges could bypass Defender when accessing Caddy through a trusted proxy whose own IP address was not blocked. This affects deployments that use Defender behind trusted proxies and expect it to enforce blocking based on the real client IP.

### Patches

The issue is fixed by making Defender prefer Caddys resolved `client_ip` request variable when it is available. Defender falls back to `RemoteAddr` only when Caddy has not provided a resolved client IP.

Users should upgrade to `v0.10.1` or later.

### Workarounds

There is no complete workaround in affected Defender versions for deployments that rely on Caddys trusted proxy client IP resolution.

Until upgrading, affected users should enforce equivalent IP blocking at the trusted proxy, CDN, load balancer, firewall, or other edge layer before traffic reaches Caddy.

Deployments where Caddy receives traffic directly from clients, without an intermediate trusted proxy, are not affected by this bypass.

## References
- https://github.com/JasonLovesDoggo/caddy-defender/security/advisories/GHSA-3h23-rrpc-3p87
- https://github.com/JasonLovesDoggo/caddy-defender/pull/139
- https://github.com/JasonLovesDoggo/caddy-defender
