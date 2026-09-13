# [H] ALPINE-CVE-2024-27983

## Summary
Severity: High
Advisory: ALPINE-CVE-2024-27983
Ecosystem: Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 8.2 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:H)
Published: 2024-04-09
Source: https://osv.dev/vulnerability/ALPINE-CVE-2024-27983
Type: osv

## Affected
- Alpine:v3.17: `nodejs` — affected >=0 <18.20.1-r0
- Alpine:v3.18: `nodejs` — affected >=0 <18.20.1-r0
- Alpine:v3.19: `nodejs` — affected >=0 <20.12.1-r0
- Alpine:v3.20: `nodejs` — affected >=0 <20.12.1-r0
- Alpine:v3.21: `nodejs` — affected >=0 <20.12.1-r0
- Alpine:v3.22: `nodejs` — affected >=0 <20.12.1-r0
- Alpine:v3.23: `nodejs` — affected >=0 <20.12.1-r0
- Alpine:v3.24: `nodejs` — affected >=0 <20.12.1-r0

## Details
An attacker can make the Node.js HTTP/2 server completely unavailable by sending a small amount of HTTP/2 frames packets with a few HTTP/2 frames inside. It is possible to leave some data in nghttp2 memory after reset when headers with HTTP/2 CONTINUATION frame are sent to the server and then a TCP connection is abruptly closed by the client triggering the Http2Session destructor while header frames are still being processed (and stored in memory) causing a race condition.

## References
- https://security.alpinelinux.org/vuln/CVE-2024-27983
