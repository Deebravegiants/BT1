# [H] BIT-envoy-2020-35470

## Summary
Severity: High
Advisory: BIT-envoy-2020-35470
Aliases: CVE-2020-35470
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-envoy-2020-35470
Type: osv

## Affected
- Bitnami: `envoy` — affected >=0 <1.16.1

## Details
Envoy before 1.16.1 logs an incorrect downstream address because it considers only the directly connected peer, not the information in the proxy protocol header. This affects situations with tcp-proxy as the network filter (not HTTP filters).

## References
- https://github.com/envoyproxy/envoy/compare/v1.16.0...v1.16.1
- https://github.com/envoyproxy/envoy/issues/14087
- https://github.com/envoyproxy/envoy/pull/14131
- https://nvd.nist.gov/vuln/detail/CVE-2020-35470
