# [C] Envoy forwards invalid Http2/Http3 downstream headers

## Summary
Severity: Critical
Advisory: BIT-envoy-2023-27491
Aliases: CVE-2023-27491, GHSA-5jmv-cw9p-f9rp
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-envoy-2023-27491
Type: osv

## Affected
- Bitnami: `envoy` — affected >=1.25.0 <1.25.3

## Details
Envoy is an open source edge and service proxy designed for cloud-native applications. Compliant HTTP/1 service should reject malformed request lines. Prior to versions 1.26.0, 1.25.3, 1.24.4, 1.23.6, and 1.22.9, There is a possibility that non compliant HTTP/1 service may allow malformed requests, potentially leading to a bypass of security policies. This issue is fixed in versions 1.26.0, 1.25.3, 1.24.4, 1.23.6, and 1.22.9.

## References
- https://datatracker.ietf.org/doc/html/rfc9113#section-8.3
- https://datatracker.ietf.org/doc/html/rfc9114#section-4.3.1
- https://github.com/envoyproxy/envoy/security/advisories/GHSA-5jmv-cw9p-f9rp
- https://www.rfc-editor.org/rfc/rfc9110#section-5.6.2
- https://nvd.nist.gov/vuln/detail/CVE-2023-27491
