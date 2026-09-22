# [H] Tilt: Cross-site WebSocket hijacking of the Tilt HUD stream

## Summary
Severity: High
Advisory: GHSA-6m68-r693-78qx
CVE: CVE-2026-55883
CWE: CWE-345
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:H/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-06-19
Source: https://github.com/advisories/GHSA-6m68-r693-78qx
Type: github-advisory

## Affected
- Go: `github.com/tilt-dev/tilt` — affected >=0.24.0 <0.37.4

## Details
## Summary
The Tilt HUD WebSocket (`/ws/view`) is gated by a CSRF token, but the token is served by an unauthenticated endpoint and the upgrader accepts any client that omits an `Origin` header. When the HUD is network-exposed, an attacker can open the HUD stream and read the developer's session state.

## Details
The upgrader accepts a connection when the `csrf` query parameter matches a process-wide token (`websocketCSRFToken`). That token is served as `text/plain` by an unauthenticated handler (`WebsocketToken`, mounted at `/api/websocket_token`), so any reachable caller can fetch it and connect to `/ws/view?csrf=<token>`. When the parameter does not match, the upgrader falls back to a same-origin check that returns true when the `Origin` header is absent, so a non-browser client that omits `Origin` is accepted anyway. The token has no per-session binding.

## Impact
An attacker who can reach the HUD listener can open the HUD WebSocket and receive the full view stream — session state, Tiltfile contents, resource statuses, and continued updates — defeating the intended anti-CSWSH protection.

### Conditions for exploitation
- Affected version in `>= 0.24.0, <= 0.37.3`.
- HUD bound to a non-loopback address (`tilt up --host 0.0.0.0`, or `TILT_HOST` set).
- Network reachability to the listener (default port `10350`).

### Not affected
- The default loopback-only bind is not reachable from the network.

## Workarounds
Use the default loopback bind (omit `--host`, unset `TILT_HOST`). No complete workaround short of upgrading for non-loopback deployments.

## References
- https://github.com/tilt-dev/tilt/security/advisories/GHSA-6m68-r693-78qx
- https://nvd.nist.gov/vuln/detail/CVE-2026-55883
- https://github.com/tilt-dev/tilt/pull/6776
- https://github.com/tilt-dev/tilt/commit/47393fba7f6ef5e305d5e814551feef8e4acbc0a
- https://github.com/tilt-dev/tilt
- https://github.com/tilt-dev/tilt/releases/tag/v0.37.4
