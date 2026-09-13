# [H] Cilium: Namespaced HTTPRoutes can redirect traffic to other namespaces

## Summary
Severity: High
Advisory: BIT-cilium-2026-56742
Aliases: BIT-cilium-operator-2026-56742, BIT-hubble-relay-2026-56742, CVE-2026-56742, GHSA-w7c2-w76w-5hmj
Ecosystem: Bitnami
Published: 2026-07-19
Source: https://osv.dev/vulnerability/BIT-cilium-2026-56742
Type: osv

## Affected
- Bitnami: `cilium` — affected >=1.19.0 <1.19.5

## Details
Cilium is a networking, observability, and security solution. Prior to 1.17.17, 1.18.11, and 1.19.5, Cilium clusters using Gateway API allow users with permissions to create or update namespaced HTTPRoutes to mirror HTTP traffic to any Service in any namespace, bypassing the ReferenceGrant authorization mechanism. Gateway API functionality is disabled by default. This issue is fixed in versions 1.17.17, 1.18.11, and 1.19.5.

## References
- https://github.com/cilium/cilium/commit/7422068aff67ac77c7dcc57aa5b9240c91333deb
- https://github.com/cilium/cilium/commit/e0b1cef513ff910323f3743e9f3e3d86721e4857
- https://github.com/cilium/cilium/commit/f23929cff682d6ed0dc158070812cb302fc0032b
- https://github.com/cilium/cilium/commit/fd47963ea394d5e8fa4a88c40a79063430c512ca
- https://github.com/cilium/cilium/releases/tag/v1.17.17
- https://github.com/cilium/cilium/releases/tag/v1.18.11
- https://github.com/cilium/cilium/releases/tag/v1.19.5
- https://github.com/cilium/cilium/security/advisories/GHSA-w7c2-w76w-5hmj
- https://nvd.nist.gov/vuln/detail/CVE-2026-56742
