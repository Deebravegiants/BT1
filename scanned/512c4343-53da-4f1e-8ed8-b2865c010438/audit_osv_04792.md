# [H] Envoy can enter an endless loop while decompressing Brotli data with extra input

## Summary
Severity: High
Advisory: BIT-envoy-2024-32976
Aliases: CVE-2024-32976, GHSA-7wp5-c2vq-4f8m
Ecosystem: Bitnami
Published: 2024-06-06
Source: https://osv.dev/vulnerability/BIT-envoy-2024-32976
Type: osv

## Affected
- Bitnami: `envoy` — affected >=1.30.0 <1.30.2

## Details
Envoy is a cloud-native, open source edge and service proxy. Envoyproxy with a Brotli filter can get into an endless loop during decompression of Brotli data with extra input.

## References
- https://github.com/envoyproxy/envoy/security/advisories/GHSA-7wp5-c2vq-4f8m
- https://nvd.nist.gov/vuln/detail/CVE-2024-32976
