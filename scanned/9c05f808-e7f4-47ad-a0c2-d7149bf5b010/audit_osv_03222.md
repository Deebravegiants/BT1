# [M] ALPINE-CVE-2025-23085

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2025-23085
Ecosystem: Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.3 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2025-02-07
Source: https://osv.dev/vulnerability/ALPINE-CVE-2025-23085
Type: osv

## Affected
- Alpine:v3.21: `nodejs` — affected >=0 <22.13.1-r0
- Alpine:v3.22: `nodejs` — affected >=0 <22.13.1-r0
- Alpine:v3.23: `nodejs` — affected >=0 <22.13.1-r0
- Alpine:v3.24: `nodejs` — affected >=0 <22.13.1-r0

## Details
A memory leak could occur when a remote peer abruptly closes the socket without sending a GOAWAY notification. Additionally, if an invalid header was detected by nghttp2, causing the connection to be terminated by the peer, the same leak was triggered. This flaw could lead to increased memory consumption and potential denial of service under certain conditions.

This vulnerability affects HTTP/2 Server users on Node.js v18.x, v20.x, v22.x and v23.x.

## References
- https://security.alpinelinux.org/vuln/CVE-2025-23085
