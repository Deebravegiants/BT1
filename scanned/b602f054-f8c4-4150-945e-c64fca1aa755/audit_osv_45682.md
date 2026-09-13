# [H] Envoy is a cloud-native high-performance edge/middle/service proxy

## Summary
Severity: High
Advisory: JLSEC-2026-2
Ecosystem: Julia
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-03-23
Source: https://osv.dev/vulnerability/JLSEC-2026-2
Type: osv

## Affected
- Julia: `nghttp2_jll` — affected >=0 <1.58.0+0

## Details
Envoy is a cloud-native high-performance edge/middle/service proxy. Envoy’s HTTP/2 codec may leak a header map and bookkeeping structures upon receiving `RST_STREAM` immediately followed by the `GOAWAY` frames from an upstream server. In nghttp2, cleanup of pending requests due to receipt of the `GOAWAY` frame skips de-allocation of the bookkeeping structure and pending compressed header. The error return [code path] is taken if connection is already marked for not sending more requests due to `GOAWAY` frame. The clean-up code is right after the return statement, causing memory leak. Denial of service through memory exhaustion. This vulnerability was patched in versions(s) 1.26.3, 1.25.8, 1.24.9, 1.23.11.

## References
- https://github.com/envoyproxy/envoy/security/advisories/GHSA-jfxv-29pc-x22r
- https://github.com/nghttp2/nghttp2/blob/e7f59406556c80904b81b593d38508591bb7523a/lib/nghttp2_session.c#L3346
