# [H] BIT-envoy-2021-28682

## Summary
Severity: High
Advisory: BIT-envoy-2021-28682
Aliases: CVE-2021-28682, GHSA-r22g-5f3x-xjgg
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-envoy-2021-28682
Type: osv

## Affected
- Bitnami: `envoy` — affected >=1.17.1 <1.17.2

## Details
An issue was discovered in Envoy through 1.71.1. There is a remotely exploitable integer overflow in which a very large grpc-timeout value leads to unexpected timeout calculations.

## References
- https://blog.envoyproxy.io
- https://github.com/envoyproxy/envoy/blob/15e3b9dbcc9aaa9d391fa8033904aad1ea1ae70d/api/envoy/api/v2/cluster.proto#L36
- https://github.com/envoyproxy/envoy/releases
- https://github.com/envoyproxy/envoy/security/advisories/GHSA-r22g-5f3x-xjgg
- https://nvd.nist.gov/vuln/detail/CVE-2021-28682
