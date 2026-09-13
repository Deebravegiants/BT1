# [H] BIT-envoy-2021-28683

## Summary
Severity: High
Advisory: BIT-envoy-2021-28683
Aliases: CVE-2021-28683
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-envoy-2021-28683
Type: osv

## Affected
- Bitnami: `envoy` — affected >=1.17.1 <1.17.2

## Details
An issue was discovered in Envoy through 1.71.1. There is a remotely exploitable NULL pointer dereference and crash in TLS when an unknown TLS alert code is received.

## References
- https://blog.envoyproxy.io
- https://github.com/envoyproxy/envoy/releases
- https://github.com/envoyproxy/envoy/security/advisories/GHSA-r22g-5f3x-xjgg
- https://github.com/envoyproxy/envoy/security/advisories/GHSA-xw4q-6pj2-5gfg
- https://nvd.nist.gov/vuln/detail/CVE-2021-28683
