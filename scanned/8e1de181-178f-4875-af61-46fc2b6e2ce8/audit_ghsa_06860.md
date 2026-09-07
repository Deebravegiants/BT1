# [H] websocket-driver-ruby: Denial of service via malformed Host header

## Summary
Severity: High
Advisory: GHSA-2x63-gw47-w4mm
CVE: CVE-2026-61666
CWE: CWE-248
Ecosystem: RubyGems
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:H (CVSS_V4)
Published: 2026-07-21
Source: https://github.com/advisories/GHSA-2x63-gw47-w4mm
Type: github-advisory

## Affected
- RubyGems: `websocket-driver` — affected >=0 <0.8.2

## Details
### Impact

If this library is used to implement a WebSocket server on top of a TCP server, by using the `WebSocket::Driver.server()` method, then a client can cause the server to crash by sending a `Host` header that is not a valid `host[:port]` string. When this happens, a `URI::InvalidURIError` exception is raised which is not caught, and this can cause the server process to crash if the application does not catch the error from the `parse()` method itself.

### Patches

The issue has been patched in version 0.8.2 by making the request parser catch `URI::InvalidURIError` and enter an error state if the `Host` header is malformed. This means the request is considered invalid and should not establish a WebSocket connection.

### Workarounds

No known workarounds exist.

### Acknowledgements

This issue was discovered and reported by Pranjali Thakur, DepthFirst Security Research Team.

## References
- https://github.com/faye/websocket-driver-ruby/security/advisories/GHSA-2x63-gw47-w4mm
- https://github.com/faye/websocket-driver-ruby/commit/7d6fd87759a2fdc83590d3b49ffa661dc53fa128
- https://github.com/faye/websocket-driver-ruby
