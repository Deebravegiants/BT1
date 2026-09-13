# [H] Midscene Bridge Server - Session Hijack via Unauthenticated WebSocket

## Summary
Severity: High
Advisory: CVE-2026-59804
CVSS: 7.5 (CVSS:4.0/AV:N/AC:H/AT:N/PR:N/UI:P/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-07-08
Source: https://osv.dev/vulnerability/CVE-2026-59804
Type: osv

## Details
Midscene Bridge Server through 1.10.3, fixed in commit 86f4118, contains a missing authentication and CORS misconfiguration vulnerability that allows unauthenticated remote attackers to hijack active bridge sessions by opening a cross-origin WebSocket connection to the local Socket.IO server, which performs no Origin header validation and requires no authentication token. Attackers can connect from any web page visited by the victim to seize the single-client slot, intercept and inject automation commands, exfiltrate command-payload data, or unconditionally terminate the server by supplying the MIDSCENE_BRIDGE_SIGNAL_KILL query parameter.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/59xxx/CVE-2026-59804.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-59804
- https://www.vulncheck.com/advisories/midscene-bridge-server-session-hijack-via-unauthenticated-websocket
- https://github.com/web-infra-dev/midscene/pull/2759
- https://github.com/web-infra-dev/midscene/commit/86f4118d1d847041c63d79e347e08c87c3f1a882
- https://github.com/web-infra-dev/midscene
- https://github.com/web-infra-dev/midscene/issues/2752
