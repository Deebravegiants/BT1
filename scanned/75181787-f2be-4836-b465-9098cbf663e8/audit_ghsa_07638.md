# [H] OpenClaw's Browser Relay /cdp websocket is missing auth which could allow cross-tab cookie access

## Summary
Severity: High
Advisory: GHSA-mr32-vwc2-5j6h
CVE: CVE-2026-28458
CWE: CWE-306
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-02-17
Source: https://github.com/advisories/GHSA-mr32-vwc2-5j6h
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=2026.1.20 <2026.2.1
- npm: `moltbot` — affected >=0

## Details
### Summary
In affected versions, the Browser Relay `/cdp` WebSocket endpoint did not require an authentication token. As a result, a website running in the browser could potentially connect to the local relay (via loopback WebSocket) and use CDP to access cookies from other open tabs and run JavaScript in the context of other tabs.

### Affected Packages / Versions
- npm: `openclaw` `>= 2026.1.20, < 2026.2.1`
- npm: `moltbot` `<= 0.1.0`

### Details
The Chrome extension Browser Relay service exposes a local WebSocket endpoint at `ws://127.0.0.1:18792/cdp` (default port) for forwarding Chrome DevTools Protocol (CDP) messages.

In affected versions, the `/cdp` upgrade path verified the TCP peer was loopback but did not require a shared secret and did not block browser-initiated cross-origin requests.

### Impact
- Potential disclosure of sensitive information (for example, session cookies from other open tabs)
- Potential JavaScript execution in the context of other open tabs

Users must have the Browser Relay extension installed and active, and must visit an untrusted site.

### Fix
`openclaw` now requires a per-instance shared secret header for Browser Relay access:
- HTTP header: `x-openclaw-relay-token`

It also rejects `/cdp` WebSocket upgrades when the Origin header is present but is not `chrome-extension://...`, and refuses `/cdp` connections unless the extension is connected.

### Fix Commit(s)
- `a1e89afcc19efd641c02b24d66d689f181ae2b5c`

### Releases
- `openclaw@2026.2.1` includes the fix.
- Latest published `openclaw` at time of writing: `2026.2.13`.

### Mitigation
- Update to `openclaw@>= 2026.2.1`.
- If you cannot update immediately, disable the Browser Relay extension / relay server and avoid visiting untrusted sites.

Thanks @johnatzeropath, @LeftenantZero, and @yueyueL for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-mr32-vwc2-5j6h
- https://nvd.nist.gov/vuln/detail/CVE-2026-28458
- https://github.com/openclaw/openclaw/commit/a1e89afcc19efd641c02b24d66d689f181ae2b5c
- https://github.com/openclaw/openclaw
- https://github.com/openclaw/openclaw/releases/tag/v2026.2.1
- https://www.vulncheck.com/advisories/openclaw-missing-authentication-in-browser-relay-cdp-websocket-endpoint
