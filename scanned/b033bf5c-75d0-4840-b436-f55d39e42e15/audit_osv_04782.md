# [M] Excessive CPU usage when URI template matcher is configured using regex in Envoy

## Summary
Severity: Medium
Advisory: BIT-envoy-2024-23323
Aliases: CVE-2024-23323, GHSA-x278-4w4x-r7ch
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-envoy-2024-23323
Type: osv

## Affected
- Bitnami: `envoy` — affected >=1.29.0 <1.29.1

## Details
Envoy is a high-performance edge/middle/service proxy. The regex expression is compiled for every request and can result in high CPU usage and increased request latency when multiple routes are configured with such matchers. This issue has been addressed in released 1.29.1, 1.28.1, 1.27.3, and 1.26.7. Users are advised to upgrade. There are no known workarounds for this vulnerability.

## References
- https://github.com/envoyproxy/envoy/commit/71eeee8f0f0132f39e402b0ee23b361ee2f4e645
- https://github.com/envoyproxy/envoy/security/advisories/GHSA-x278-4w4x-r7ch
- https://nvd.nist.gov/vuln/detail/CVE-2024-23323
