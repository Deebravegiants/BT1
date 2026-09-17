# [H] Envoy vulnerable to CORS filter segfault when origin header is removed

## Summary
Severity: High
Advisory: BIT-envoy-2023-35943
Aliases: CVE-2023-35943, GHSA-mc6h-6j9x-v3gq
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-envoy-2023-35943
Type: osv

## Affected
- Bitnami: `envoy` — affected >=1.26.0 <1.26.4

## Details
Envoy is an open source edge and service proxy designed for cloud-native applications. Prior to versions 1.27.0, 1.26.4, 1.25.9, 1.24.10, and 1.23.12, the CORS filter will segfault and crash Envoy when the `origin` header is removed and deleted between `decodeHeaders`and `encodeHeaders`. Versions 1.27.0, 1.26.4, 1.25.9, 1.24.10, and 1.23.12 have a fix for this issue. As a workaround, do not remove the `origin` header in the Envoy configuration.

## References
- https://github.com/envoyproxy/envoy/security/advisories/GHSA-mc6h-6j9x-v3gq
- https://nvd.nist.gov/vuln/detail/CVE-2023-35943
