# [H] Envoy allows large requests and responses to cause TCP connection pool crash

## Summary
Severity: High
Advisory: BIT-envoy-2025-62409
Aliases: CVE-2025-62409, GHSA-pq33-4jxh-hgm3
Ecosystem: Bitnami
Published: 2025-10-21
Source: https://osv.dev/vulnerability/BIT-envoy-2025-62409
Type: osv

## Affected
- Bitnami: `envoy` — affected >=1.36.0 <1.36.1

## Details
Envoy is a cloud-native, open source edge and service proxy. Prior to 1.36.1, 1.35.5, 1.34.9, and 1.33.10, large requests and responses can potentially trigger TCP connection pool crashes due to flow control management in Envoy. It will happen when the connection is closing but upstream data is still coming, resulting in a buffer watermark callback nullptr reference. The vulnerability impacts TCP proxy and HTTP 1 & 2 mixed use cases based on ALPN. This vulnerability is fixed in 1.36.1, 1.35.5, 1.34.9, and 1.33.10.

## References
- https://github.com/envoyproxy/envoy/security/advisories/GHSA-pq33-4jxh-hgm3
- https://nvd.nist.gov/vuln/detail/CVE-2025-62409
