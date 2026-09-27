# [M] ha-mcp OAuth 2.1 DCR mode enables network reconnaissance via an error oracle

## Summary
Severity: Medium
Advisory: GHSA-fmfg-9g7c-3vq7
CVE: CVE-2026-32111
CWE: CWE-918
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-03-12
Source: https://github.com/advisories/GHSA-fmfg-9g7c-3vq7
Type: github-advisory

## Affected
- PyPI: `ha-mcp` — affected >=0 <7.0.0

## Details
### Summary

The ha-mcp OAuth consent form (beta feature) accepts a user-supplied `ha_url` and makes a server-side HTTP request to `{ha_url}/api/config` with no URL validation. An unauthenticated attacker can submit arbitrary URLs to perform internal network reconnaissance via an error oracle. Two additional code paths in OAuth tool calls (REST and WebSocket) are affected by the same primitive.

The primary deployment method (private URL with pre-configured `HOMEASSISTANT_TOKEN`) is not affected.

### Details

**Code path 1 — Consent form validation** (reported)

When a user submits the OAuth consent form, `_validate_ha_credentials()` (`provider.py`) makes a server-side GET request to `{ha_url}/api/config` with no scheme, IP, or domain validation. Different exception types produce distinct error messages, creating an error oracle:

| Outcome | Message returned | Information leaked |
|---------|------------------|--------------------|
| `ConnectError` | "Could not connect..." | Host down or port closed |
| `TimeoutException` | "Connection timed out..." | Host up, port filtered |
| HTTP 401 | "Invalid access token..." | Service alive, requires auth |
| HTTP 403 | "Access forbidden..." | Service alive, forbidden |
| HTTP ≥ 400 | "Failed to connect: HTTP {N}" | Service alive, exact status |

An attacker can drive the flow programmatically: register a client via open DCR (`POST /register`), initiate authorization, extract a `txn_id`, and submit arbitrary `ha_url` values. No user interaction required.

**Code path 2 — REST tool calls with forged token**

OAuth access tokens are stateless base64-encoded JSON payloads (`{"ha_url": "...", "ha_token": "..."}`). Since tokens are not signed, an attacker can forge a token with an arbitrary `ha_url`. REST tool calls then make HTTP requests to hardcoded HA API paths on that host (`/config`, `/states`, `/services`, etc.). JSON responses are returned to the caller.

In practice, path control is limited — most endpoints use absolute paths that ignore the `ha_url` path component. Useful exfiltration requires the target to return JSON at HA API paths, which is unlikely for non-HA services.

**Code path 3 — WebSocket tool calls with forged token**

The same forged token triggers WebSocket connections to `ws://{ha_url}/api/websocket`. The client follows the HA WebSocket handshake protocol (waits for `auth_required`, sends `auth`, expects `auth_ok`). Non-HA targets fail at the protocol level and return nothing useful. Realistic exploitation is limited to pivoting to another HA instance on the internal network.

### Impact

**Confirmed:** Internal network reconnaissance via error oracle (all 3 code paths). An attacker can map reachable hosts and open ports from the server's network position.

### Scope

OAuth mode is a **beta** feature, documented separately in `docs/OAUTH.md` and not part of the main setup instructions. The standard deployment method (pre-configured `HOMEASSISTANT_URL` and `HOMEASSISTANT_TOKEN`) is not affected.

### Fix

Upgrade to 7.0.0

## References
- https://github.com/homeassistant-ai/ha-mcp/security/advisories/GHSA-fmfg-9g7c-3vq7
- https://nvd.nist.gov/vuln/detail/CVE-2026-32111
- https://github.com/homeassistant-ai/ha-mcp
