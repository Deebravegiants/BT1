# [M] Kubewarden: Cross-namespace data exfiltration via deprecated host callback binding

## Summary
Severity: Medium
Advisory: GHSA-6r7f-3fwq-hq74
CVE: CVE-2026-29773
CWE: CWE-863
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-03-09
Source: https://github.com/advisories/GHSA-6r7f-3fwq-hq74
Type: github-advisory

## Affected
- Go: `github.com/kubewarden/kubewarden-controller` — affected >=0 <1.33.0

## Details
### Impact

Kubewarden is a policy engine for Kubernetes. Kubewarden cluster operators can grant permissions to users to deploy namespaced AdmissionPolicies and AdmissionPolicyGroups in their Namespaces. One of Kubewarden promises is that configured users can deploy namespaced policies in a safe manner, without privilege escalation.

An attacker with privileged "AdmissionPolicy" create permissions (which isn't the default) could make use of 3 deprecated host-callback APIs: `kubernetes/ingresses`, `kubernetes/namespaces`, `kubernetes/services`.
The attacker can craft a policy that exercises these deprecated API calls and would allow them read access to Ingresses, Namespaces, and Services resources respectively.

This attack is read-only, there is no write capability and no access to Secrets, ConfigMaps, or other resource types beyond these three. The attacker could read for example:
- Namespace names and labels.
- Services across all namespaces with ClusterIPs and ports to reveal cluster internal topology.
- Ingresses across all namespaces with hostnames and routing rules.

### Patches
The vulnerable, already deprecated host-capabilities (`kubernetes/ingresses`, `kubernetes/namespaces`, `kubernetes/services`)
have been removed.

The removed calls were not being exercised by any Kubewarden SDK.

These host-callbacks had already been superseded for a long time by `kubewarden/kubernetes/list_resources_by_namespace`, `kubewarden/kubernetes/list_resources`, and `kubewarden/kubernetes/get_resource`. They provide similar capabilities while being more fine-grained, performant, and gated through our context-aware permissions feature. These current host-capabilities are part of the Kubernetes capabilities listed in our [docs](https://docs.kubewarden.io/reference/spec/host-capabilities/kubernetes).

### Workarounds
Kubewarden operators can update the policy-server image used by their PolicyServers to tag `:v1.33.0`.
Alternatively, Kubewarden operators can temporarily reduce the permissions of users to prevent them from creating or updating existing namespaced AdmissionPolicies or AdmissionPolicyGroups.

## References
- https://github.com/kubewarden/kubewarden-controller/security/advisories/GHSA-6r7f-3fwq-hq74
- https://nvd.nist.gov/vuln/detail/CVE-2026-29773
- https://github.com/kubewarden/kubewarden-controller/pull/1519
- https://github.com/kubewarden/kubewarden-controller/commit/4e41b60ae44902d82d94101bac93fb77cae65651
- https://github.com/kubewarden/kubewarden-controller
