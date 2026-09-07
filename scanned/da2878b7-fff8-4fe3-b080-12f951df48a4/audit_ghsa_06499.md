# [M] websocket-driver: Memory exhaustion via abuse of protocol length headers

## Summary
Severity: Medium
Advisory: GHSA-ghhp-3qvg-889p
CVE: CVE-2026-54463
CWE: CWE-400, CWE-770
Ecosystem: RubyGems
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:L/SC:N/SI:N/SA:L (CVSS_V4)
Published: 2026-07-15
Source: https://github.com/advisories/GHSA-ghhp-3qvg-889p
Type: github-advisory

## Affected
- RubyGems: `websocket-driver` — affected >=0 <0.8.1

## Details
### Impact

The frame format in draft versions of the WebSocket protocol includes a length header that allows an arbitrarily large integer to be encoded as a sequence of bytes with the high bit set. By sending an indefinite sequence of bytes with values `0x80` or above, a server or client can make the other peer parse these bytes into an ever-growing integer. Since Ruby integers are arbitrary precision, this can be used to make a WebSocket connection consume an unbounded amount of memory and lead to the host process running out of memory.

### Patches

The issue has been patched in version 0.8.1. All users should upgrade to this version.

### Workarounds

No known workarounds exist.

### Acknowledgements

This issue was discovered and reported by Pranjali Thakur, DepthFirst Security Research Team.

## References
- https://github.com/faye/websocket-driver-ruby/security/advisories/GHSA-ghhp-3qvg-889p
- https://nvd.nist.gov/vuln/detail/CVE-2026-54463
- https://github.com/faye/websocket-driver-ruby/commit/d0141f041f6e3677a951255d547a313e732ccbe0
- https://github.com/faye/websocket-driver-ruby
- https://github.com/faye/websocket-driver-ruby/releases/tag/0.8.1
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/websocket-driver/CVE-2026-54463.yml
- https://www.cve.org/CVERecord/SearchResults?query=CVE-2026-54463
