# [H] BIT-envoy-2020-12603

## Summary
Severity: High
Advisory: BIT-envoy-2020-12603
Aliases: CVE-2020-12603, GHSA-pc38-4q6c-85p6
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-envoy-2020-12603
Type: osv

## Affected
- Bitnami: `envoy` — affected >=1.14.2 <1.14.3

## Details
Envoy version 1.14.2, 1.13.2, 1.12.4 or earlier may consume excessive amounts of memory when proxying HTTP/2 requests or responses with many small (i.e. 1 byte) data frames.

## References
- https://github.com/envoyproxy/envoy-setec/issues/80
- https://github.com/envoyproxy/envoy/security/advisories/GHSA-pc38-4q6c-85p6
- https://nvd.nist.gov/vuln/detail/CVE-2020-12603
