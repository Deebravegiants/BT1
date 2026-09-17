# [M] AppFlowy-Cloud through 0.9.64 Cross-Workspace Collab Read via WebSocket

## Summary
Severity: Medium
Advisory: CVE-2026-85622
CVSS: 6.0 (CVSS:4.0/AV:N/AC:H/AT:P/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-09-04
Source: https://osv.dev/vulnerability/CVE-2026-85622
Type: osv

## Details
AppFlowy-Cloud through 0.9.64 fails to validate workspace membership when establishing WebSocket connections in the establish_ws_connection_v2 handler, allowing authenticated users to bind sessions to workspaces they do not belong to. Attackers can send sync Manifest messages with victim object identifiers to read full document or database state from collaborations in other workspaces without victim involvement.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/85xxx/CVE-2026-85622.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-85622
- https://www.vulncheck.com/advisories/appflowy-cloud-through-0.9.64-cross-workspace-collab-read-via-websocket
- https://github.com/AppFlowy-IO/AppFlowy-Cloud/issues/1629
- https://github.com/AppFlowy-IO/AppFlowy-Cloud
- https://github.com/AppFlowy-IO/AppFlowy-Cloud/blob/0.9.64/src/api/ws.rs
