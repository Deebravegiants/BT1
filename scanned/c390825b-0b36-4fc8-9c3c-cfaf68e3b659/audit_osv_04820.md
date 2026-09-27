# [H] Envoy Zstd Decompressor: Ratio Check at Wrong Loop Depth lead to memory explosion

## Summary
Severity: High
Advisory: BIT-envoy-2026-48044
Aliases: CVE-2026-48044, GHSA-m3p9-47wh-88wg
Ecosystem: Bitnami
Published: 2026-06-30
Source: https://osv.dev/vulnerability/BIT-envoy-2026-48044
Type: osv

## Affected
- Bitnami: `envoy` — affected >=1.38.0 <1.38.1

## Details
Envoy is an open source edge and service proxy designed for cloud-native applications. From 1.23.0 until 1.35.11, 1.36.7, 1.37.3, and 1.38.1, a  vulnerability has been identified in Envoy's zstd decompressor implementation (ZstdDecompressorImpl). When zstd decompression is enabled, processing a specially crafted, highly compressed zstd payload can lead to massive memory allocation. An attacker can exploit this to cause severe memory exhaustion, potentially resulting in an Out-Of-Memory (OOM) kill and Denial of Service (DoS) for the Envoy proxy. This vulnerability is fixed in 1.35.11, 1.36.7, 1.37.3, and 1.38.1.

## References
- https://github.com/envoyproxy/envoy/security/advisories/GHSA-m3p9-47wh-88wg
- https://nvd.nist.gov/vuln/detail/CVE-2026-48044
