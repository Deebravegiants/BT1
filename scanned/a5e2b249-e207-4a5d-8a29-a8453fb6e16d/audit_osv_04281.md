# [M] Cilium may unexpectedly allow ingress traffic from the local namespace when a Kubernetes NetworkPolicy is configured with an ipBlock match

## Summary
Severity: Medium
Advisory: BIT-cilium-2026-56743
Aliases: BIT-cilium-operator-2026-56743, BIT-hubble-relay-2026-56743, CVE-2026-56743, GHSA-fm8w-2m5w-9j7r, GO-2026-6367
Ecosystem: Bitnami
Published: 2026-07-19
Source: https://osv.dev/vulnerability/BIT-cilium-2026-56743
Type: osv

## Affected
- Bitnami: `cilium` — affected >=1.19.0 <1.19.5

## Details
Cilium is a networking, observability, and security solution. From 1.19.0 to 1.19.4, standard Kubernetes NetworkPolicy specifications using CIDR-based ipBlock rules without pod or namespace selectors erroneously generate a wildcard namespace allow rule when Cilium is configured with a custom clusterName rather than the default any value. The parser incorrectly instantiates a pod selector on selectorless peer definitions, allowing traffic from other workloads in the same namespace as the subject of the policy. This issue is fixed in version 1.19.5.

## References
- https://github.com/cilium/cilium/commit/1c84ae3b58a7cd54f7ee355e6c524c82f620eae8
- https://github.com/cilium/cilium/commit/bacea640404c0805c23515353dc1681c5bf35171
- https://github.com/cilium/cilium/pull/46305
- https://github.com/cilium/cilium/pull/46456
- https://github.com/cilium/cilium/releases/tag/v1.19.5
- https://github.com/cilium/cilium/security/advisories/GHSA-fm8w-2m5w-9j7r
- https://nvd.nist.gov/vuln/detail/CVE-2026-56743
