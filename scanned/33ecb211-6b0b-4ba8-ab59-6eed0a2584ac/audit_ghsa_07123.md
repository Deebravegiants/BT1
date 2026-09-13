# [M] websocket-driver: Resource limit bypass via message compression

## Summary
Severity: Medium
Advisory: GHSA-mp7j-qc5w-4988
CVE: CVE-2026-54490
CWE: CWE-770
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:N/VI:N/VA:L/SC:N/SI:N/SA:L (CVSS_V4)
Published: 2026-07-15
Source: https://github.com/advisories/GHSA-mp7j-qc5w-4988
Type: github-advisory

## Affected
- npm: `websocket-driver` — affected >=0 <0.7.5

## Details
### Impact

If this library is used in tandem with the `permessage-deflate` extension, a WebSocket server or client can be made to accept messages that are larger than the configured maximum message size. This is because this limit is checked against the message frames' length headers, which give the size of the compressed data, not the size after decompression. This can lead to applications accepting larger messages than expected and exceeding their intended resource usage.

### Patches

The issue has been patched in version 0.7.5, by checking the length of messages after they are processed by incoming extensions. All users should upgrade to this version.

### Workarounds

No known workarounds exist.

### Acknowledgements

This issue was discovered and reported by Pranjali Thakur, DepthFirst Security Research Team.

## References
- https://github.com/faye/websocket-driver-node/security/advisories/GHSA-mp7j-qc5w-4988
- https://github.com/faye/websocket-driver-node
- https://github.com/faye/websocket-driver-node/releases/tag/0.7.5
