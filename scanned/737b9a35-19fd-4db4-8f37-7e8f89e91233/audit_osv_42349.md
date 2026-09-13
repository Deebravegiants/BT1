# [C] FreeRDP before 3.29.0 WebSocket Ping Buffer Over-disclosure

## Summary
Severity: Critical
Advisory: CVE-2026-67292
Aliases: GHSA-8v6m-2cmc-chx9
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-01
Source: https://osv.dev/vulnerability/CVE-2026-67292
Type: osv

## Details
FreeRDP before 3.29.0 contains a buffer over-disclosure vulnerability in the gateway WebSocket transport (libfreerdp/core/gateway/websocket.c). The client's Pong reply reuses a fixed 1024-byte response stream whose length is not sealed to the actual received Ping payload, so a malicious gateway/WebSocket peer sending a non-empty Ping control frame causes the client to reply with an overlong Pong that discloses bytes beyond the received payload (the peer receives the masking key and can unmask the reply). A zero-length Ping reaches an assertion and terminates the client (denial of service).

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/67xxx/CVE-2026-67292.json
- https://github.com/FreeRDP/FreeRDP/security/advisories/GHSA-8v6m-2cmc-chx9
- https://nvd.nist.gov/vuln/detail/CVE-2026-67292
- https://www.vulncheck.com/advisories/freerdp-before-websocket-ping-buffer-over-disclosure
- https://github.com/FreeRDP/FreeRDP/commit/f3b4347105114fe7453828736bea069999af319f
