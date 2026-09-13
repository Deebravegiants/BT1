# [M] Kubernetes users may update Pod labels to bypass network policy

## Summary
Severity: Medium
Advisory: GHSA-gj2r-phwg-6rww
CVE: CVE-2023-39347
CWE: CWE-345
Ecosystem: Go
CVSS: CVSS:3.1/AV:A/AC:L/PR:L/UI:N/S:C/C:L/I:N/A:L (CVSS_V3)
Published: 2023-09-26
Source: https://github.com/advisories/GHSA-gj2r-phwg-6rww
Type: github-advisory

## Affected
- Go: `github.com/cilium/cilium` — affected >=1.13.0 <1.13.7
- Go: `github.com/cilium/cilium` — affected >=1.14.0 <1.14.2
- Go: `github.com/cilium/cilium` — affected >=0 <1.12.14

## Details
### Impact

An attacker with the ability to update pod labels can cause Cilium to apply incorrect network policies.

This issue arises due to the fact that on pod update, Cilium incorrectly uses user-provided pod labels to select the policies which apply to the workload in question.

This can affect:

* Cilium network policies that use the namespace, service account or cluster constructs to restrict traffic
* Cilium clusterwide network policies that use Cilium namespace labels to select the Pod
* Kubernetes network policies

Non-existent construct names can be provided, which bypass all network policies applicable to the construct. For example, providing a pod with a non-existent namespace as the value of the `io.kubernetes.pod.namespace` label results in none of the namespaced CiliumNetworkPolicies applying to the pod in question.

This attack requires the attacker to have [Kubernetes API Server access](https://docs.cilium.io/en/latest/security/threat-model/#kubernetes-api-server-attacker), as described in the Cilium Threat Model.

### Patches

This issue affects:

- Cilium <= v1.14.1
- Cilium <= v1.13.6
- Cilium <= v1.12.13

This issue has been resolved in:

- Cilium v1.14.2
- Cilium v1.13.7
- Cilium v1.12.14

### Workarounds

An admission webhook can be used to prevent pod label updates to the `k8s:io.kubernetes.pod.namespace` and `io.cilium.k8s.policy.*` keys.

### Acknowledgements
The Cilium community has worked together with members of Palantir and Isovalent to prepare these mitigations. Special thanks to @odinuge for reporting this issue and to @nebril for the fix.

### For more information
If you have any questions or comments about this advisory, please reach out on [Slack](https://docs.cilium.io/en/latest/community/community/#slack).

If you think you have found a vulnerability in Cilium, we strongly encourage you to report it to our private security mailing list – [security@cilium.io](mailto:security@cilium.io) – first, before disclosing them in any public forums. This is a private mailing list where only members of the Cilium internal security team are subscribed to, and is treated as top priority.

## References
- https://github.com/cilium/cilium/security/advisories/GHSA-gj2r-phwg-6rww
- https://nvd.nist.gov/vuln/detail/CVE-2023-39347
- https://docs.cilium.io/en/latest/security/threat-model/#kubernetes-api-server-attacker
- https://github.com/cilium/cilium
