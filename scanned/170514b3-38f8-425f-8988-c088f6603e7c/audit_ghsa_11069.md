# [M] OpenClaw's Node role device-identity bypass allows unauthorized node.event injection

## Summary
Severity: Medium
Advisory: GHSA-rv2q-f2h5-6xmg
CVE: CVE-2026-32001
CWE: CWE-863
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-03-03
Source: https://github.com/advisories/GHSA-rv2q-f2h5-6xmg
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.2.22

## Details
### Summary
A client authenticated with a shared gateway token could connect as `role=node` without device identity/pairing, then call `node.event` to trigger `agent.request` and `voice.transcript` flows.

### Affected Packages / Versions
- Package: npm `openclaw`
- Affected versions: `<= 2026.2.21-2`
- Patched version: `2026.2.22` (planned next release)

### Details
The WebSocket connect path allowed device-less bypass whenever shared auth succeeded. That bypass did not restrict role, so a client could claim `role=node` with no device identity and still pass handshake auth. Because `node.event` is node-role allowed, this enabled unauthorized node event injection into agent-trigger flows.

### Impact
Unauthorized `node.event` injection can trigger agent execution and voice transcript flows for clients that only hold the shared gateway token, without node device pairing.

### Remediation
Upgrade to `2026.2.22` (or newer) once published. The fix requires device identity for `role=node` connects, even when shared-token auth succeeds.

### Fix Commit(s)
- ddcb2d79b17bf2a42c5037d8aeff1537a12b931e

### Release Process Note
`patched_versions` is pre-set to the planned next release so once npm release `2026.2.22` is out, advisory publish is a single step.

OpenClaw thanks @tdjackey for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-rv2q-f2h5-6xmg
- https://nvd.nist.gov/vuln/detail/CVE-2026-32001
- https://github.com/openclaw/openclaw/commit/ddcb2d79b17bf2a42c5037d8aeff1537a12b931e
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-node-role-device-identity-bypass-via-websocket-authentication
