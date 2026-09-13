# [M] Cilium vulnerable to bypass of namespace restrictions in CiliumNetworkPolicy 

## Summary
Severity: Medium
Advisory: GHSA-4xp2-w642-7mcx
CVE: CVE-2023-41333
CWE: CWE-306
Ecosystem: Go
CVSS: CVSS:3.1/AV:A/AC:L/PR:H/UI:N/S:C/C:L/I:N/A:H (CVSS_V3)
Published: 2023-09-27
Source: https://github.com/advisories/GHSA-4xp2-w642-7mcx
Type: github-advisory

## Affected
- Go: `github.com/cilium/cilium` — affected >=1.14.0 <1.14.2
- Go: `github.com/cilium/cilium` — affected >=1.13.0 <1.13.7
- Go: `github.com/cilium/cilium` — affected >=0 <1.12.14

## Details
### Impact

An attacker with the ability to create or modify CiliumNetworkPolicy objects in a particular namespace is able to affect traffic on an entire Cilium cluster, potentially bypassing policy enforcement in other namespaces.

By using a crafted `endpointSelector` that uses the `DoesNotExist` operator on the `reserved:init` label, the attacker can create policies that bypass namespace restrictions and affect the entire Cilium cluster. This includes potentially allowing or denying all traffic.

This attack requires API server access, as described in the [Kubernetes API Server Attacker](https://docs.cilium.io/en/stable/security/threat-model/#kubernetes-api-server-attacker) section of the Cilium Threat Model.

### Patches

This issue was patched in https://github.com/cilium/cilium/pull/28007

This issue affects:

- Cilium <= v1.14.1
- Cilium <= v1.13.6
- Cilium <= v1.12.13

This issue has been resolved in:

- Cilium v1.14.2
- Cilium v1.13.7
- Cilium v1.12.14

### Workarounds

An admission webhook can be used to prevent the use of `endpointSelector`s that use the `DoesNotExist` operator on the `reserved:init` label in CiliumNetworkPolicies.

### Acknowledgements
The Cilium community has worked together with members of Palantir and Isovalent to prepare these mitigations. Special thanks to @odinuge for reporting this issue and @joestringer for the fix.

### For more information
If you have any questions or comments about this advisory, please reach out on [Slack](https://docs.cilium.io/en/latest/community/community/#slack).

If you think you have found a vulnerability in Cilium, we strongly encourage you to report it to our private security mailing list at [security@cilium.io](mailto:security@cilium.io) first, before disclosing it in any public forum. This is a private mailing list for Cilium's internal security team, and your report will be treated as top priority.

## References
- https://github.com/cilium/cilium/security/advisories/GHSA-4xp2-w642-7mcx
- https://nvd.nist.gov/vuln/detail/CVE-2023-41333
- https://github.com/cilium/cilium/pull/28007
- https://docs.cilium.io/en/stable/security/threat-model/#kubernetes-api-server-attacker
- https://github.com/cilium/cilium
