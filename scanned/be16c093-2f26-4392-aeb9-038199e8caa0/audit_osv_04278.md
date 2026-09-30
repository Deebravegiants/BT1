# [M] East-west traffic not subject to egress policy enforcement for requests via Gateway API load balancers

## Summary
Severity: Medium
Advisory: BIT-cilium-2025-30162
Aliases: BIT-cilium-operator-2025-30162, BIT-hubble-relay-2025-30162, CVE-2025-30162, GHSA-24qp-4xx8-3jvj, GO-2025-3560
Ecosystem: Bitnami
Published: 2025-03-26
Source: https://osv.dev/vulnerability/BIT-cilium-2025-30162
Type: osv

## Affected
- Bitnami: `cilium` — affected >=1.15.0 <1.17.2

## Details
Cilium is a networking, observability, and security solution with an eBPF-based dataplane. For Cilium users who use Gateway API for Ingress for some services and use LB-IPAM or BGP for LB Service implementation and use network policies to block egress traffic from workloads in a namespace to workloads in other namespaces, egress traffic from workloads covered by such network policies to LoadBalancers configured by `Gateway` resources will incorrectly be allowed. LoadBalancer resources not deployed via a Gateway API configuration are not affected by this issue. This issue affects: Cilium v1.15 between v1.15.0 and v1.15.14 inclusive, v1.16 between v1.16.0 and v1.16.7 inclusive, and v1.17 between v1.17.0 and v1.17.1 inclusive. This issue is fixed in Cilium v1.15.15, v1.16.8, and v1.17.2. A Clusterwide Cilium Network Policy can be used to work around this issue for users who are unable to upgrade.

## References
- https://docs.cilium.io/en/stable/network/lb-ipam
- https://github.com/cilium/cilium/security/advisories/GHSA-24qp-4xx8-3jvj
- https://github.com/cilium/proxy/pull/1172
- https://nvd.nist.gov/vuln/detail/CVE-2025-30162
