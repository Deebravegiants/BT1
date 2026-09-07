# [M] OpenClaw's gateway tokenless Tailscale auth applied to HTTP routes

## Summary
Severity: Medium
Advisory: GHSA-hff7-ccv5-52f8
CVE: CVE-2026-32045
CWE: CWE-290
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-03
Source: https://github.com/advisories/GHSA-hff7-ccv5-52f8
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.2.21

## Details
### Summary
When tokenless Tailscale auth is enabled, OpenClaw should only allow forwarded-header auth for Control UI websocket authentication on trusted hosts. In affected versions, that tokenless path could also be used by HTTP gateway auth call sites, which could bypass token/password requirements for HTTP routes in trusted-network deployments.

### Affected Packages / Versions
- Package: `openclaw` (npm)
- Affected range: `<= 2026.2.19-2` (latest published npm version as of February 21, 2026)
- Patched in: planned `2026.2.21` release

### Impact
Deployments relying on token/password for HTTP gateway routes could be downgraded to tokenless behavior when Tailscale header auth is enabled. This weakens expected HTTP route authentication boundaries even in trusted-host network setups.

Per SECURITY.md, this does not affect the recommended setup: keep the Gateway loopback-only (or otherwise within a trusted host/network boundary), use Tailscale serve/funnel for remote access, and keep tokenless Tailscale auth scoped to Control UI websocket login.

### Fix
- Added an explicit auth-surface gate (`allowTailscaleHeaderAuth`, default `false`) in gateway auth.
- Enabled tokenless Tailscale header auth only for Control UI websocket authentication.
- Kept HTTP gateway auth call sites on token/password auth paths.
- Added regression coverage for HTTP-vs-websocket behavior and Tailscale header handling.

### Fix Commit(s)
- `356d61aacfa5b0f1d5830716ec59d70682a3e7b8`

### Release Process Note
`patched_versions` is pre-set to the planned next release (`2026.2.21`) so once npm release is published, this advisory can be published directly without further field edits.

OpenClaw thanks @zpbrent for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-hff7-ccv5-52f8
- https://nvd.nist.gov/vuln/detail/CVE-2026-32045
- https://github.com/openclaw/openclaw/commit/356d61aacfa5b0f1d5830716ec59d70682a3e7b8
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-authentication-bypass-in-http-gateway-routes-via-tokenless-tailscale-auth
