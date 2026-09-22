# [H] Excessive CPU utilization when closing HTTP/2 streams

## Summary
Severity: High
Advisory: BIT-envoy-2021-32778
Aliases: CVE-2021-32778, GHSA-3xh3-33v5-chcc
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-envoy-2021-32778
Type: osv

## Affected
- Bitnami: `envoy` — affected >=1.19.0 <1.19.1

## Details
Envoy is an open source L7 proxy and communication bus designed for large modern service oriented architectures. In affected versions envoy’s procedure for resetting a HTTP/2 stream has O(N^2) complexity, leading to high CPU utilization when a large number of streams are reset. Deployments are susceptible to Denial of Service when Envoy is configured with high limit on H/2 concurrent streams. An attacker wishing to exploit this vulnerability would require a client opening and closing a large number of H/2 streams. Envoy versions 1.19.1, 1.18.4, 1.17.4, 1.16.5 contain fixes to reduce time complexity of resetting HTTP/2 streams. As a workaround users may limit the number of simultaneous HTTP/2 dreams for upstream and downstream peers to a low number, i.e. 100.

## References
- https://github.com/envoyproxy/envoy/security/advisories/GHSA-3xh3-33v5-chcc
- https://www.envoyproxy.io/docs/envoy/v1.19.0/version_history/version_history
- https://nvd.nist.gov/vuln/detail/CVE-2021-32778
