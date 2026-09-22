# [M] OpenClaw's web tools strict URL guard could lose DNS pinning when env proxy is configured

## Summary
Severity: Medium
Advisory: GHSA-8mvx-p2r9-r375
CVE: CVE-2026-22181
CWE: CWE-367, CWE-918
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:H/VI:L/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-03
Source: https://github.com/advisories/GHSA-8mvx-p2r9-r375
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.3.2

## Details
### Summary
`openclaw` web tools strict URL fetch paths could lose DNS pinning when environment proxy variables are configured (`HTTP_PROXY`/`HTTPS_PROXY`/`ALL_PROXY`, including lowercase variants).

In affected builds, strict URL checks (for example `web_fetch` and citation redirect resolution) validated one destination during SSRF guard checks, but runtime connection routing could proceed through an env-proxy dispatcher.

### Affected Packages / Versions
- Package: `openclaw` (npm)
- Vulnerable version range: `<= 2026.3.1`
- Latest published npm version at triage time (2026-03-02): `2026.3.1`
- Patched versions: `>= 2026.3.2` (released)

### Technical Details
The SSRF guard performed hostname resolution and policy checks, then selected a request dispatcher.

When env proxy settings were present, strict web-tool flows could use `EnvHttpProxyAgent` instead of the DNS-pinned dispatcher. This created a destination-binding gap between check-time resolution and connect-time routing.

The fix keeps DNS pinning on strict/untrusted web-tool URL paths and limits env-proxy bypass behavior to trusted/operator-controlled endpoints via an explicit dangerous opt-in.

### Impact
In deployments with env proxy variables configured, attacker-influenced URLs from web tools could be routed through proxy behavior instead of strict pinned-destination routing, which could allow access to internal/private targets reachable from that proxy environment.

### Mitigations
Before upgrading, operators can reduce exposure by clearing proxy env vars for OpenClaw runtime processes or disabling `web_fetch` / `web_search` where untrusted URL input is possible.

### Fix Commit(s)
- `345abf0b2e0f43b0f229e96f252ebf56f1e5549e`

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-8mvx-p2r9-r375
- https://nvd.nist.gov/vuln/detail/CVE-2026-22181
- https://github.com/openclaw/openclaw/commit/345abf0b2e0f43b0f229e96f252ebf56f1e5549e
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-dns-pinning-bypass-via-environment-proxy-configuration-in-web-fetch
