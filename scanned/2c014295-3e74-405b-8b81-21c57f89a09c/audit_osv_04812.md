# [M] Envoy crashes if multiple unexpected ext_proc responses are packed into one gRPC message

## Summary
Severity: Medium
Advisory: BIT-envoy-2026-47207
Aliases: CVE-2026-47207, GHSA-68cv-hq5f-g6xv
Ecosystem: Bitnami
Published: 2026-06-29
Source: https://osv.dev/vulnerability/BIT-envoy-2026-47207
Type: osv

## Affected
- Bitnami: `envoy` — affected >=1.38.0 <1.38.3

## Details
Envoy is an open source edge and service proxy designed for cloud-native applications. From 1.34.0 until 1.35.13, 1.36.9, 1.37.5, and 1.38.3, Envoy crashes if an ext_proc server sends a single gRPC message containing multiple, specially crafted ProcessingResponse messages. This can occur when the first response in the batch causes the gRPC stream object to be destroyed, leading to a use-after-free error when Envoy attempts to process subsequent responses in the same gRPC message. This vulnerability is fixed in 1.35.13, 1.36.9, 1.37.5, and 1.38.3.

## References
- https://github.com/envoyproxy/envoy/security/advisories/GHSA-68cv-hq5f-g6xv
- https://nvd.nist.gov/vuln/detail/CVE-2026-47207
