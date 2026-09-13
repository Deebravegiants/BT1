# [M] ALPINE-CVE-2026-21714

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2026-21714
Ecosystem: Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.3 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2026-03-30
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-21714
Type: osv

## Affected
- Alpine:v3.21: `nodejs` — affected >=0 <22.22.2-r0
- Alpine:v3.22: `nodejs` — affected >=0 <22.22.2-r0
- Alpine:v3.23: `nodejs` — affected >=0 <24.14.1-r0
- Alpine:v3.24: `nodejs` — affected >=0 <24.14.1-r0

## Details
A memory leak occurs in Node.js HTTP/2 servers when a client sends WINDOW_UPDATE frames on stream 0 (connection-level) that cause the flow control window to exceed the maximum value of 2³¹-1. The server correctly sends a GOAWAY frame, but the Http2Session object is never cleaned up.

This vulnerability affects HTTP2 users on Node.js 20, 22, 24 and 25.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-21714
