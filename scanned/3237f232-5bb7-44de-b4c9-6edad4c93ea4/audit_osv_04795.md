# [C] Envoy Proxy use after free when route hash policy is configured with cookie attributes

## Summary
Severity: Critical
Advisory: BIT-envoy-2024-39305
Aliases: CVE-2024-39305, GHSA-fp35-g349-h66f
Ecosystem: Bitnami
Published: 2024-07-03
Source: https://osv.dev/vulnerability/BIT-envoy-2024-39305
Type: osv

## Affected
- Bitnami: `envoy` — affected >=1.30.0 <1.30.4

## Details
Envoy is a cloud-native, open source edge and service proxy. Prior to versions 1.30.4, 1.29.7, 1.28.5, and 1.27.7. Envoy references already freed memory when route hash policy is configured with cookie attributes. Note that this vulnerability has been fixed in the open as the effect would be immediately apparent if it was configured. Memory allocated for holding attribute values is freed after configuration was parsed. During request processing Envoy will attempt to copy content of de-allocated memory into request cookie header. This can lead to arbitrary content of Envoy's memory to be sent to the upstream service or abnormal process termination. This vulnerability is fixed in Envoy versions v1.30.4, v1.29.7, v1.28.5, and v1.27.7. As a workaround, do not use cookie attributes in route action hash policy.

## References
- https://github.com/envoyproxy/envoy/commit/02a06681fbe0e039b1c7a9215257a7537eddb518
- https://github.com/envoyproxy/envoy/commit/50b384cb203a1f2894324cbae64b6d9bc44cce45
- https://github.com/envoyproxy/envoy/commit/99b6e525fb9f6f6f19a0425f779bc776f121c7e5
- https://github.com/envoyproxy/envoy/commit/b7f509607ad860fd6a63cde4f7d6f0197f9f63bb
- https://github.com/envoyproxy/envoy/security/advisories/GHSA-fp35-g349-h66f
- https://nvd.nist.gov/vuln/detail/CVE-2024-39305
