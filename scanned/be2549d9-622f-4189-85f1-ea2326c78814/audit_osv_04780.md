# [H] Envoy vulnerable to HTTP/2 memory leak in nghttp2 codec

## Summary
Severity: High
Advisory: BIT-envoy-2023-35945
Aliases: CVE-2023-35945, GHSA-jfxv-29pc-x22r
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-envoy-2023-35945
Type: osv

## Affected
- Bitnami: `envoy` — affected >=1.26.0 <1.26.3

## Details
Envoy is a cloud-native high-performance edge/middle/service proxy. Envoy’s HTTP/2 codec may leak a header map and bookkeeping structures upon receiving `RST_STREAM` immediately followed by the `GOAWAY` frames from an upstream server. In nghttp2, cleanup of pending requests due to receipt of the `GOAWAY` frame skips de-allocation of the bookkeeping structure and pending compressed header. The error return [code path] is taken if connection is already marked for not sending more requests due to `GOAWAY` frame. The clean-up code is right after the return statement, causing memory leak. Denial of service through memory exhaustion. This vulnerability was patched in versions(s) 1.26.3, 1.25.8, 1.24.9, 1.23.11.

## References
- https://github.com/envoyproxy/envoy/security/advisories/GHSA-jfxv-29pc-x22r
- https://github.com/nghttp2/nghttp2/blob/e7f59406556c80904b81b593d38508591bb7523a/lib/nghttp2_session.c#L3346
- https://nvd.nist.gov/vuln/detail/CVE-2023-35945
