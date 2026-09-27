# [M] BIT-node-2026-21714

## Summary
Severity: Medium
Advisory: BIT-node-2026-21714
Aliases: BIT-node-min-2026-21714, CVE-2026-21714
Ecosystem: Bitnami
Published: 2026-04-06
Source: https://osv.dev/vulnerability/BIT-node-2026-21714
Type: osv

## Affected
- Bitnami: `node` — affected >=25.0.0 <25.8.2

## Details
A memory leak occurs in Node.js HTTP/2 servers when a client sends WINDOW_UPDATE frames on stream 0 (connection-level) that cause the flow control window to exceed the maximum value of 2³¹-1. The server correctly sends a GOAWAY frame, but the Http2Session object is never cleaned up.

This vulnerability affects HTTP2 users on Node.js 20, 22, 24 and 25.

## References
- https://nodejs.org/en/blog/vulnerability/march-2026-security-releases
- https://nvd.nist.gov/vuln/detail/CVE-2026-21714
