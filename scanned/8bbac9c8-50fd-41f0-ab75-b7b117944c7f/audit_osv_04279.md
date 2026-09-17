# [M] Node based network policies may incorrectly allow workload traffic

## Summary
Severity: Medium
Advisory: BIT-cilium-2025-30163
Aliases: BIT-cilium-operator-2025-30163, BIT-hubble-relay-2025-30163, CVE-2025-30163, GHSA-c6pf-2v8j-96mc, GO-2025-3561
Ecosystem: Bitnami
Published: 2025-03-26
Source: https://osv.dev/vulnerability/BIT-cilium-2025-30163
Type: osv

## Affected
- Bitnami: `cilium` — affected >=1.16.0 <1.17.2

## Details
Cilium is a networking, observability, and security solution with an eBPF-based dataplane. Node based network policies (`fromNodes` and `toNodes`) will incorrectly permit traffic to/from non-node endpoints that share the labels specified in `fromNodes` and `toNodes` sections of network policies. Node based network policy is disabled by default in Cilium. This issue affects: Cilium v1.16 between v1.16.0 and v1.16.7 inclusive and v1.17 between v1.17.0 and v1.17.1 inclusive. This issue is fixed in Cilium v1.16.8 and v1.17.2. Users can work around this issue by ensuring that the labels used in `fromNodes` and `toNodes` fields are used exclusively by nodes and not by other endpoints.

## References
- https://docs.cilium.io/en/stable/security/policy/language/#node-based
- https://github.com/cilium/cilium/pull/36657
- https://github.com/cilium/cilium/security/advisories/GHSA-c6pf-2v8j-96mc
- https://nvd.nist.gov/vuln/detail/CVE-2025-30163
