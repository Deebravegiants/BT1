# [H] OpenClaw: Untrusted web origins can obtain authenticated operator.admin access in trusted-proxy mode

## Summary
Severity: High
Advisory: GHSA-5wcw-8jjv-m286
CVE: CVE-2026-32302
CWE: CWE-346
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-03-12
Source: https://github.com/advisories/GHSA-5wcw-8jjv-m286
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.3.11

## Details
## Summary
In affected versions of `openclaw`, browser-originated WebSocket connections could bypass origin validation when `gateway.auth.mode` was set to `trusted-proxy` and the request arrived with proxy headers. A page served from an untrusted origin could connect through a trusted reverse proxy, inherit proxy-authenticated identity, and establish a privileged operator session.

## Impact
This issue affects deployments that expose the Gateway behind a trusted reverse proxy and rely on browser origin checks such as `controlUi.allowedOrigins` to restrict browser access. An attacker who can cause a victim browser to load a malicious page that can reach the proxy endpoint could establish a cross-site WebSocket connection and call privileged Gateway methods.

In verified impact, the attacker-origin page was able to request `operator.admin` and successfully call `config.get`, exposing sensitive configuration. Depending on the deployment, the same authenticated operator path could also permit other privileged reads or mutations available to operator-class callers.

## Affected Packages and Versions
- Package: `openclaw` (npm)
- Affected versions: `< 2026.3.11`
- Fixed in: `2026.3.11`

## Technical Details
The WebSocket handshake logic treated proxy-delivered requests as exempt from the generic browser origin check whenever an `Origin` header was present alongside proxy headers. In `trusted-proxy` mode, that exemption allowed browser-originated connections to skip the normal origin-validation path even though they were still browser requests.

Because trusted-proxy authentication can produce a shared authenticated operator context, the affected path could retain requested operator scopes after the handshake. That made the browser origin check the missing boundary between an untrusted origin and an authenticated operator-class session.

## Fix
OpenClaw now enforces browser origin validation for any browser-originated WebSocket connection regardless of whether proxy headers are present. The fix shipped in `openclaw@2026.3.11`.

Fixed commit: `ebed3bbde1a72a1aaa9b87b63b91e7c04a50036b`
Release tag: `v2026.3.11`

## Workarounds
Upgrade to `2026.3.11` or later.

If you cannot upgrade immediately, avoid exposing browser-reachable Gateway WebSocket endpoints in `trusted-proxy` mode to untrusted origins, and ensure reverse-proxy/browser reachability is restricted to trusted origins only.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-5wcw-8jjv-m286
- https://nvd.nist.gov/vuln/detail/CVE-2026-32302
- https://github.com/openclaw/openclaw/commit/ebed3bbde1a72a1aaa9b87b63b91e7c04a50036b
- https://github.com/openclaw/openclaw
- https://github.com/openclaw/openclaw/releases/tag/v2026.3.11
