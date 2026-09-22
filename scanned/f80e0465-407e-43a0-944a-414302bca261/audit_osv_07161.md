# [M] BIT-node-2025-23085

## Summary
Severity: Medium
Advisory: BIT-node-2025-23085
Aliases: BIT-node-min-2025-23085, CVE-2025-23085
Ecosystem: Bitnami
Published: 2025-02-11
Source: https://osv.dev/vulnerability/BIT-node-2025-23085
Type: osv

## Affected
- Bitnami: `node` — affected >=23.0.0 <23.8.0

## Details
A memory leak could occur when a remote peer abruptly closes the socket without sending a GOAWAY notification. Additionally, if an invalid header was detected by nghttp2, causing the connection to be terminated by the peer, the same leak was triggered. This flaw could lead to increased memory consumption and potential denial of service under certain conditions.

This vulnerability affects HTTP/2 Server users on Node.js v18.x, v20.x, v22.x and v23.x.

## References
- https://nodejs.org/en/blog/vulnerability/january-2025-security-releases
- https://lists.debian.org/debian-lts-announce/2025/02/msg00031.html
- https://nvd.nist.gov/vuln/detail/CVE-2025-23085
- https://security.netapp.com/advisory/ntap-20250321-0003/
