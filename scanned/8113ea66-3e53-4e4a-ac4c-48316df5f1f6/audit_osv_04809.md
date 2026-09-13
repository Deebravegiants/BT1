# [M] Envoy forwards early CONNECT data in TCP proxy mode

## Summary
Severity: Medium
Advisory: BIT-envoy-2025-64763
Aliases: CVE-2025-64763, GHSA-rj35-4m94-77jh
Ecosystem: Bitnami
Published: 2025-12-06
Source: https://osv.dev/vulnerability/BIT-envoy-2025-64763
Type: osv

## Affected
- Bitnami: `envoy` — affected >=1.36.0 <1.36.3

## Details
Envoy is a high-performance edge/middle/service proxy. In 1.33.12, 1.34.10, 1.35.6, 1.36.2, and earlier, when Envoy is configured in TCP proxy mode to handle CONNECT requests, it accepts client data before issuing a 2xx response and forwards that data to the upstream TCP connection. If a forwarding proxy upstream from Envoy then responds with a non-2xx status, this can cause a de-synchronized CONNECT tunnel state. By default Envoy continues to allow early CONNECT data to avoid disrupting existing deployments. The envoy.reloadable_features.reject_early_connect_data runtime flag can be set to reject CONNECT requests that send data before a 2xx response when intermediaries upstream from Envoy may reject establishment of a CONNECT tunnel.

## References
- https://github.com/envoyproxy/envoy/security/advisories/GHSA-rj35-4m94-77jh
- https://nvd.nist.gov/vuln/detail/CVE-2025-64763
