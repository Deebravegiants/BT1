# [M] Envoy may crash when a large request body is processed in Lua filter

## Summary
Severity: Medium
Advisory: BIT-envoy-2023-27492
Aliases: CVE-2023-27492, GHSA-wpc2-2jp6-ppg2
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-envoy-2023-27492
Type: osv

## Affected
- Bitnami: `envoy` — affected >=1.25.0 <1.25.3

## Details
Envoy is an open source edge and service proxy designed for cloud-native applications. Prior to versions 1.26.0, 1.25.3, 1.24.4, 1.23.6, and 1.22.9, the Lua filter is vulnerable to denial of service. Attackers can send large request bodies for routes that have Lua filter enabled and trigger crashes.

As of versions versions 1.26.0, 1.25.3, 1.24.4, 1.23.6, and 1.22.9, Envoy no longer invokes the Lua coroutine if the filter has been reset. As a workaround for those whose Lua filter is buffering all requests/ responses, mitigate by using the buffer filter to avoid triggering the local reply in the Lua filter.

## References
- https://github.com/envoyproxy/envoy/security/advisories/GHSA-wpc2-2jp6-ppg2
- https://nvd.nist.gov/vuln/detail/CVE-2023-27492
