# [C] Envoy doesn't escape HTTP header values

## Summary
Severity: Critical
Advisory: BIT-envoy-2023-27493
Aliases: CVE-2023-27493, GHSA-w5w5-487h-qv8q
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-envoy-2023-27493
Type: osv

## Affected
- Bitnami: `envoy` — affected >=1.25.0 <1.25.3

## Details
Envoy is an open source edge and service proxy designed for cloud-native applications. Prior to versions 1.26.0, 1.25.3, 1.24.4, 1.23.6, and 1.22.9, Envoy does not sanitize or escape request properties when generating request headers. This can lead to characters that are illegal in header values to be sent to the upstream service. In the worst case, it can cause upstream service to interpret the original request as two pipelined requests, possibly bypassing the intent of Envoy’s security policy. Versions 1.26.0, 1.25.3, 1.24.4, 1.23.6, and 1.22.9 contain a patch. As a workaround, disable adding request headers based on the downstream request properties, such as downstream certificate properties.

## References
- https://github.com/envoyproxy/envoy/security/advisories/GHSA-w5w5-487h-qv8q
- https://nvd.nist.gov/vuln/detail/CVE-2023-27493
