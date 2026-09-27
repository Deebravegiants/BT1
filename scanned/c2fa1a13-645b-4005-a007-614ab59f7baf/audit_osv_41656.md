# [M] Centrifugo: Decompression bomb DoS via permessage-deflate in unidirectional WebSocket transport

## Summary
Severity: Medium
Advisory: CVE-2026-62963
Aliases: GHSA-q6mr-3g59-5m8x
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-07-16
Source: https://osv.dev/vulnerability/CVE-2026-62963
Type: osv

## Details
Centrifugo is an open-source scalable real-time messaging server. Prior to 6.8.4, Centrifugo unidirectional WebSocket transport with uni_websocket.compression enabled enforced uni_websocket.message_size_limit against compressed wire-frame length in internal/websocket/conn.go advanceFrame, but ReadMessage used io.ReadAll after decompression without an output cap, allowing unauthenticated requests to /connection/uni_websocket to trigger large memory and CPU consumption. This issue is fixed in version 6.8.4.

## References
- https://github.com/centrifugal/centrifugo/releases/tag/v6.8.4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/62xxx/CVE-2026-62963.json
- https://github.com/centrifugal/centrifugo/security/advisories/GHSA-q6mr-3g59-5m8x
- https://nvd.nist.gov/vuln/detail/CVE-2026-62963
- https://github.com/centrifugal/centrifugo/commit/46d40e4ac3a5446c9745f8b219197166ae12a6e5
- https://github.com/centrifugal/centrifugo/pull/1162
