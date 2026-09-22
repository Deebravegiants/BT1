# [H] BIT-envoy-2020-35471

## Summary
Severity: High
Advisory: BIT-envoy-2020-35471
Aliases: CVE-2020-35471
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-envoy-2020-35471
Type: osv

## Affected
- Bitnami: `envoy` — affected >=0 <1.16.1

## Details
Envoy before 1.16.1 mishandles dropped and truncated datagrams, as demonstrated by a segmentation fault for a UDP packet size larger than 1500.

## References
- https://github.com/envoyproxy/envoy/compare/v1.16.0...v1.16.1
- https://github.com/envoyproxy/envoy/issues/14113
- https://github.com/envoyproxy/envoy/pull/14122
- https://nvd.nist.gov/vuln/detail/CVE-2020-35471
