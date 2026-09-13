# [H] Envoy crashes when using an address type that isn’t supported by the OS

## Summary
Severity: High
Advisory: BIT-envoy-2024-23325
Aliases: CVE-2024-23325, GHSA-5m7c-mrwr-pm26
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-envoy-2024-23325
Type: osv

## Affected
- Bitnami: `envoy` — affected >=1.29.0 <1.29.1

## Details
Envoy is a high-performance edge/middle/service proxy. Envoy crashes in Proxy protocol when using an address type that isn’t supported by the OS. Envoy is susceptible to crashing on a host with IPv6 disabled and a listener config with proxy protocol enabled when it receives a request where the client presents its IPv6 address.  It is valid for a client to present its IPv6 address to a target server even though the whole chain is connected via IPv4. This issue has been addressed in released 1.29.1, 1.28.1, 1.27.3, and 1.26.7. Users are advised to upgrade. There are no known workarounds for this vulnerability.

## References
- https://github.com/envoyproxy/envoy/commit/bacd3107455b8d387889467725eb72aa0d5b5237
- https://github.com/envoyproxy/envoy/security/advisories/GHSA-5m7c-mrwr-pm26
- https://nvd.nist.gov/vuln/detail/CVE-2024-23325
