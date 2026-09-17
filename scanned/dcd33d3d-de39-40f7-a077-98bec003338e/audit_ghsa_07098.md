# [C] websocket-driver: Message corruption via abuse of protocol length headers

## Summary
Severity: Critical
Advisory: GHSA-xv26-6w52-cph6
CVE: CVE-2026-54466
CWE: CWE-130
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:H/SA:N (CVSS_V4)
Published: 2026-07-15
Source: https://github.com/advisories/GHSA-xv26-6w52-cph6
Type: github-advisory

## Affected
- npm: `websocket-driver` — affected >=0 <0.7.5

## Details
### Impact

The frame format in draft versions of the WebSocket protocol includes a length header that allows an arbitrarily large integer to be encoded as a sequence of bytes with the high bit set. By sending an indefinite sequence of bytes with values `0x80` or above, a client can make the server parse these bytes into an ever-growing integer. Since JavaScript numbers are 64-bit floating point values, this number will eventually lose precision and lead to the subsequent payload being parsed incorrectly.

### Patches

The issue has been patched in version 0.7.5 by rejecting the message if the length header exceeds the configured maximum message length. All users should upgrade to this version.

### Workarounds

No known workarounds exist.

### Acknowledgements

This issue was discovered and reported by Pranjali Thakur, DepthFirst Security Research Team.

## References
- https://github.com/faye/websocket-driver-node/security/advisories/GHSA-xv26-6w52-cph6
- https://github.com/faye/websocket-driver-node
- https://github.com/faye/websocket-driver-node/releases/tag/0.7.5
