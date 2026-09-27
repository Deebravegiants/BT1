# [H] Crash in proxy protocol when command type of LOCAL in Envoy

## Summary
Severity: High
Advisory: BIT-envoy-2024-23327
Aliases: CVE-2024-23327, GHSA-4h5x-x9vh-m29j
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-envoy-2024-23327
Type: osv

## Affected
- Bitnami: `envoy` — affected >=1.29.0 <1.29.1

## Details
Envoy is a high-performance edge/middle/service proxy. When PPv2 is enabled both on a listener and subsequent cluster, the Envoy instance will segfault when attempting to craft the upstream PPv2 header. This occurs when the downstream request has a command type of LOCAL and does not have the protocol block. This issue has been addressed in releases 1.29.1, 1.28.1, 1.27.3, and 1.26.7. Users are advised to upgrade. There are no known workarounds for this vulnerability.

## References
- https://github.com/envoyproxy/envoy/commit/63895ea8e3cca9c5d3ab4c5c128ed1369969d54a
- https://github.com/envoyproxy/envoy/security/advisories/GHSA-4h5x-x9vh-m29j
- https://nvd.nist.gov/vuln/detail/CVE-2024-23327
