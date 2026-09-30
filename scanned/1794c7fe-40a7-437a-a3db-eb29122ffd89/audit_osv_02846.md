# [H] ALPINE-CVE-2023-35945

## Summary
Severity: High
Advisory: ALPINE-CVE-2023-35945
Ecosystem: Alpine:v3.15, Alpine:v3.16, Alpine:v3.17
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-07-13
Source: https://osv.dev/vulnerability/ALPINE-CVE-2023-35945
Type: osv

## Affected
- Alpine:v3.15: `nghttp2` — affected >=0 <1.46.0-r1
- Alpine:v3.16: `nghttp2` — affected >=0 <1.47.0-r1
- Alpine:v3.17: `nghttp2` — affected >=0 <1.51.0-r1

## Details
Envoy is a cloud-native high-performance edge/middle/service proxy. Envoy’s HTTP/2 codec may leak a header map and bookkeeping structures upon receiving `RST_STREAM` immediately followed by the `GOAWAY` frames from an upstream server. In nghttp2, cleanup of pending requests due to receipt of the `GOAWAY` frame skips de-allocation of the bookkeeping structure and pending compressed header. The error return [code path] is taken if connection is already marked for not sending more requests due to `GOAWAY` frame. The clean-up code is right after the return statement, causing memory leak. Denial of service through memory exhaustion. This vulnerability was patched in versions(s) 1.26.3, 1.25.8, 1.24.9, 1.23.11.

## References
- https://security.alpinelinux.org/vuln/CVE-2023-35945
