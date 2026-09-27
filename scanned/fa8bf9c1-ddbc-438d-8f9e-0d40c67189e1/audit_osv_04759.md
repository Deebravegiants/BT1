# [H] Null pointer dereference in envoy

## Summary
Severity: High
Advisory: BIT-envoy-2021-43824
Aliases: CVE-2021-43824, GHSA-vj5m-rch8-5r2p
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-envoy-2021-43824
Type: osv

## Affected
- Bitnami: `envoy` — affected >=1.21.0 <1.21.1

## Details
Envoy is an open source edge and service proxy, designed for cloud-native applications. In affected versions a crafted request crashes Envoy when a CONNECT request is sent to JWT filter configured with regex match. This provides a denial of service attack vector. The only workaround is to not use regex in the JWT filter. Users are advised to upgrade.

## References
- https://github.com/envoyproxy/envoy/commit/9371333230b1a6e1be2eccf4868771e11af6253a
- https://github.com/envoyproxy/envoy/security/advisories/GHSA-vj5m-rch8-5r2p
- https://nvd.nist.gov/vuln/detail/CVE-2021-43824
