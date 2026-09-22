# [M] Cilium L7 proxy may bypass Kubernetes NetworkPolicy for same-node traffic

## Summary
Severity: Medium
Advisory: GHSA-hxv8-4j4r-cqgv
CVE: CVE-2026-33726
CWE: CWE-284, CWE-863
Ecosystem: Go
CVSS: CVSS:3.1/AV:A/AC:L/PR:L/UI:N/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-03-26
Source: https://github.com/advisories/GHSA-hxv8-4j4r-cqgv
Type: github-advisory

## Affected
- Go: `github.com/cilium/cilium` — affected >=0 <1.17.14
- Go: `github.com/cilium/cilium` — affected >=1.18.0 <1.18.8
- Go: `github.com/cilium/cilium` — affected >=1.19.0 <1.19.2

## Details
### Impact

Ingress [Network Policies](https://docs.cilium.io/en/stable/network/kubernetes/policy/#network-policy) are not enforced for traffic from pods to L7 Services ([Envoy](https://docs.cilium.io/en/stable/network/servicemesh/l7-traffic-management), GAMMA) with a local backend on the same node, when [Per-Endpoint Routing](https://docs.cilium.io/en/stable/network/concepts/routing/#routing) is enabled and [BPF Host Routing](https://docs.cilium.io/en/stable/operations/performance/tuning/#ebpf-host-routing) is disabled.

Per-Endpoint Routing is disabled by default, but is automatically enabled in deployments using cloud IPAM, including Cilium ENI on EKS (`eni.enabled`), AlibabaCloud ENI (`alibabacloud.enabled`), Azure IPAM (`azure.enabled`, but not AKS BYOCNI), and some GKE deployments (`gke.enabled`; managed offerings such as GKE Dataplane V2 may use different defaults). It is typically not enabled in tunneled deployments, and chaining deployments are not affected. In practice, Amazon EKS with Cilium ENI mode is likely the most common affected environment.

### Patches

This issue was fixed by #44693.

This issue affects:

* Cilium v1.19 between v1.19.0 and v1.19.1 inclusive
* Cilium v1.18 between v1.18.0 and v1.18.7 inclusive
* All versions of Cilium prior to v1.17.13

This issue is fixed in:

* Cilium v1.19.2
* Cilium v1.18.8
* Cilium v1.17.14

### Workarounds

Disclaimer: There is currently no officially verified or comprehensive workaround for this issue. The only option would be to disable per-endpoint routes, but this will likely cause disruptions to ongoing connections, and potential conflicts if running in cloud providers.

### Acknowledgements

The Cilium community has worked together with members of the Northflank and Isovalent teams to prepare these mitigations. Cilium thanks @sudeephb and @Champ-Goblem for reporting the issue and to @smagnani96 and @julianwiedmann for helping with the resolution.

### For more information

Anyone who believes a vulnerability affecting Cilium has been found is strongly encouraged to report it to the security mailing list at security@cilium.io. This is a private mailing list for the Cilium security team, and any such report will be treated as top priority. Please also address any comments or questions on this advisory to the same mailing list.

## References
- https://github.com/cilium/cilium/security/advisories/GHSA-hxv8-4j4r-cqgv
- https://nvd.nist.gov/vuln/detail/CVE-2026-33726
- https://github.com/cilium/cilium/pull/44693
- https://docs.cilium.io/en/stable/network/concepts/routing/#routing
- https://docs.cilium.io/en/stable/network/kubernetes/policy/#network-policy
- https://docs.cilium.io/en/stable/network/servicemesh/l7-traffic-management
- https://docs.cilium.io/en/stable/operations/performance/tuning/#ebpf-host-routing
- https://github.com/cilium/cilium
