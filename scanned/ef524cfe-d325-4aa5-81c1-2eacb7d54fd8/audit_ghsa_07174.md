# [H] Coder's workspace agent API insecure redirect handling allowed cross-agent file read and write

## Summary
Severity: High
Advisory: GHSA-qrwj-vh9x-gw5v
CWE: CWE-863, CWE-918
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:L (CVSS_V3)
Published: 2026-07-06
Source: https://github.com/advisories/GHSA-qrwj-vh9x-gw5v
Type: github-advisory

## Affected
- Go: `github.com/coder/coder/v2` — affected >=2.34.0 <2.34.4
- Go: `github.com/coder/coder/v2` — affected >=2.33.0 <2.33.10
- Go: `github.com/coder/coder/v2` — affected >=2.30.0 <2.32.9
- Go: `github.com/coder/coder/v2` — affected >=2.27.0 <2.29.19

## Details
### Summary

`agentConn.apiClient()` used the default redirect behavior of `http.Client` while its custom transport dialed the host from the request URL as long as the port was the workspace agent HTTP API port (`4`). Agent tailnet IPs are deterministic from agent UUIDs, so a malicious workspace agent could return a redirect to another agent's tailnet IP and cause the control-plane client to send the follow-up workspace agent API request to the victim agent instead of the intended agent.

Redirects that preserve the method and body, such as HTTP 307 and 308, allow replay of write and process-start requests. HTTP 301, 302 and 303 redirects only convert POST requests to GET requests, so they are sufficient to demonstrate redirected reads but not write or command-execution primitives.

### Impact

An authenticated user with a running workspace and control of a modified workspace agent can redirect workspace agent API requests made to their agent toward another online workspace agent reachable on the tailnet. If the attacker knows the victim agent UUID, they can derive the victim's tailnet IP and target the victim's file APIs to read or write files as the victim workspace user.

In affected versions that expose the workspace agent process API, the same primitive can be chained to command execution as the victim workspace user by writing a payload through the redirected file API and then redirecting a process-start request to execute it. This crosses workspace and tenant boundaries.

### Patches

The fix disables automatic redirect following for workspace agent API clients and pins all workspace agent API dials to the intended agent's deterministic tailnet address. Requests whose URL host does not match the intended agent are rejected instead of being dialed.

The fix was backported to all supported release lines:

| Release line | Patched version |
|---|---|
| 2.34 | [v2.34.4](https://github.com/coder/coder/releases/tag/v2.34.4) |
| 2.33 | [v2.33.10](https://github.com/coder/coder/releases/tag/v2.33.10) |
| 2.32 | [v2.32.9](https://github.com/coder/coder/releases/tag/v2.32.9) |
| 2.29 (ESR) | [v2.29.19](https://github.com/coder/coder/releases/tag/v2.29.19) |

### Workarounds

None. Upgrading is required.

### Resources
- Fix: #26600

## References
- https://github.com/coder/coder/security/advisories/GHSA-qrwj-vh9x-gw5v
- https://github.com/coder/coder/pull/26600
- https://github.com/coder/coder
