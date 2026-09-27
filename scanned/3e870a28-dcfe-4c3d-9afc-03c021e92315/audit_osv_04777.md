# [M] Envoy's gRPC access log crash caused by the listener draining

## Summary
Severity: Medium
Advisory: BIT-envoy-2023-35942
Aliases: CVE-2023-35942, GHSA-69vr-g55c-v2v4
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-envoy-2023-35942
Type: osv

## Affected
- Bitnami: `envoy` — affected >=1.26.0 <1.26.4

## Details
Envoy is an open source edge and service proxy designed for cloud-native applications. Prior to versions 1.27.0, 1.26.4, 1.25.9, 1.24.10, and 1.23.12, gRPC access loggers using listener's global scope can cause a `use-after-free` crash when the listener is drained. Versions 1.27.0, 1.26.4, 1.25.9, 1.24.10, and 1.23.12 have a fix for this issue. As a workaround, disable gRPC access log or stop listener update.

## References
- https://github.com/envoyproxy/envoy/security/advisories/GHSA-69vr-g55c-v2v4
- https://nvd.nist.gov/vuln/detail/CVE-2023-35942
