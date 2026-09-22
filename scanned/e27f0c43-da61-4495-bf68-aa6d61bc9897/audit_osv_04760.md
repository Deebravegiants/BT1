# [H] Crash when tunneling TCP over HTTP in Envoy

## Summary
Severity: High
Advisory: BIT-envoy-2021-43826
Aliases: CVE-2021-43826, GHSA-cmx3-fvgf-83mf
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-envoy-2021-43826
Type: osv

## Affected
- Bitnami: `envoy` — affected >=1.21.0 <1.21.1

## Details
Envoy is an open source edge and service proxy, designed for cloud-native applications. In affected versions of Envoy a crash occurs when configured for :ref:`upstream tunneling <envoy_v3_api_field_extensions.filters.network.tcp_proxy.v3.TcpProxy.tunneling_config>` and the downstream connection disconnects while the the upstream connection or http/2 stream is still being established. There are no workarounds for this issue. Users are advised to upgrade.

## References
- https://github.com/envoyproxy/envoy/commit/ce0ae309057a216aba031aff81c445c90c6ef145
- https://github.com/envoyproxy/envoy/security/advisories/GHSA-cmx3-fvgf-83mf
- https://nvd.nist.gov/vuln/detail/CVE-2021-43826
