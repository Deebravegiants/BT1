# [H] BIT-envoy-2021-29258

## Summary
Severity: High
Advisory: BIT-envoy-2021-29258
Aliases: CVE-2021-29258
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-envoy-2021-29258
Type: osv

## Affected
- Bitnami: `envoy` — affected >=1.17.1 <1.17.2

## Details
An issue was discovered in Envoy 1.14.0. There is a remotely exploitable crash for HTTP2 Metadata, because an empty METADATA map triggers a Reachable Assertion.

## References
- https://blog.envoyproxy.io
- https://github.com/envoyproxy/envoy-setec/pull/230
- https://github.com/envoyproxy/envoy/releases/tag/v1.14.0
- https://github.com/envoyproxy/envoy/security/advisories/GHSA-rqvq-hxw5-776j
- https://github.com/envoyproxy/envoy/security/advisories/GHSA-xw4q-6pj2-5gfg
- https://nvd.nist.gov/vuln/detail/CVE-2021-29258
