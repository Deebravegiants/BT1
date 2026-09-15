# [H] Envoy ext auth can be bypassed when Proxy protocol filter sets invalid UTF-8 metadata

## Summary
Severity: High
Advisory: BIT-envoy-2024-23324
Aliases: CVE-2024-23324, GHSA-gq3v-vvhj-96j6
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-envoy-2024-23324
Type: osv

## Affected
- Bitnami: `envoy` — affected >=1.29.0 <1.29.1

## Details
Envoy is a high-performance edge/middle/service proxy. External authentication can be bypassed by downstream connections. Downstream clients can force invalid gRPC requests to be sent to ext_authz, circumventing ext_authz checks when failure_mode_allow is set to true. This issue has been addressed in released 1.29.1, 1.28.1, 1.27.3, and 1.26.7. Users are advised to upgrade. There are no known workarounds for this vulnerability.

## References
- https://github.com/envoyproxy/envoy/commit/29989f6cc8bfd8cd2ffcb7c42711eb02c7a5168a
- https://github.com/envoyproxy/envoy/security/advisories/GHSA-gq3v-vvhj-96j6
- https://nvd.nist.gov/vuln/detail/CVE-2024-23324
