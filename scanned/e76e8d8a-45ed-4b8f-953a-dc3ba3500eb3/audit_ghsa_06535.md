# [M] websocket-driver: Memory exhaustion in HTTP header parser

## Summary
Severity: Medium
Advisory: GHSA-8j3g-f24p-4mpw
CVE: CVE-2026-54465
CWE: CWE-400, CWE-770
Ecosystem: RubyGems
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:N/VI:N/VA:L/SC:N/SI:N/SA:L (CVSS_V4)
Published: 2026-07-15
Source: https://github.com/advisories/GHSA-8j3g-f24p-4mpw
Type: github-advisory

## Affected
- RubyGems: `websocket-driver` — affected >=0 <0.8.1

## Details
### Impact

If this library is used to implement a WebSocket server on top of a TCP server (rather than an HTTP server or framework) using the `WebSocket::Driver.server()` method, or, if it is used to complement a WebSocket client, then a peer can make a single connection consume an unbounded amount of memory by sending an HTTP request or response with a never-ending list of headers. This can lead to the receiving process running out of memory.

### Patches

The issue has been patched in version 0.8.1, by limiting the total size of HTTP request/response lines and headers accepted by the parser to 32 kB. All users should upgrade to this version.

### Workarounds

No known workarounds exist.

### Acknowledgements

This issue was discovered and reported by Pranjali Thakur, DepthFirst Security Research Team.

## References
- https://github.com/faye/websocket-driver-ruby/security/advisories/GHSA-8j3g-f24p-4mpw
- https://nvd.nist.gov/vuln/detail/CVE-2026-54465
- https://github.com/faye/websocket-driver-ruby/commit/17b569f232896e71d458404ccf4854f80e987710
- https://github.com/faye/websocket-driver-ruby
- https://github.com/faye/websocket-driver-ruby/releases/tag/0.8.1
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/websocket-driver/CVE-2026-54465.yml
- https://www.cve.org/CVERecord/SearchResults?query=CVE-2026-54465
