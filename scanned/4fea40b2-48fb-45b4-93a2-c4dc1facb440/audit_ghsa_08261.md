# [M] Kubewarden vulnerable to RBAC Reconnaissance via unchecked can_i host capability call

## Summary
Severity: Medium
Advisory: GHSA-wqcw-g35j-j578
CVE: CVE-2026-42541
CWE: CWE-862
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-05-05
Source: https://github.com/advisories/GHSA-wqcw-g35j-j578
Type: github-advisory

## Affected
- Go: `github.com/kubewarden/kubewarden-controller` — affected >=0 <1.35.0

## Details
### Impact
Kubewarden is a policy engine for Kubernetes. Kubewarden cluster operators can grant permissions to users to deploy namespaced AdmissionPolicies and AdmissionPolicyGroups in their Namespaces. One of Kubewarden promises is that configured users can deploy namespaced policies in a safe manner, without privilege escalation.

An attacker with privileged AdmissionPolicy or AdmissionPolicyGroup create permissions (which isn't the default) can craft a policy that makes use of the `can_i` host callback. The callback issues a SubjectAccessReview (SAR) requests to enumerate RBAC permissions of any user or service account across the cluster. Three operations on the host capabilities `kubewarden/kubernetes` binding enforce the context-aware allow-list via `can_access_kubernetes_resource()`:

- `list_resources_by_namespace`
- `list_resources_all`
- `get_resource`

However, `can_i` does not perform that check and forwards the request directly to the callback handler, which executes a real SubjectAccessReview using policy-server privileges. This creates a policy-level authorization gap: `can_i` is effectively usable even when the policy has no context-aware resource grant.

This is an information disclosure / reconnaissance issue, and not direct workload data exfiltration. The attacker learns permission information, such as whether specific service accounts can "get secrets", "create pods", or "bind clusterroles" in chosen namespaces.

### Patches

Cluster Operators, if providing their users with privileges to deploy AdmissionPolicies or AdmissionPolicygroups (which isn't the default), must then also deploy PolicyServers with reduced permissions for host capability calls. This includes the PolicyServer `default`. 
For that, make use of the new feature in v1.35:
- For custom PolicyServers: Set the new `PolicyServer.spec.namespacedPoliciesCapabilities` , for example to an empty list `[]` which doesn't allow any capability.
- For the `default` PolicyServer, set the `.Values.policyServer.namespacedPoliciesCapabilities` , for example to an empty list `[]` which doesn't allow any capability. 

Also, if needed, they must ensure that those namespaced AdmissionPolicies or AdmissionPolicygroups are scheduled in the PolicyServers with reduced permissions.
For that, they could make use of the new [ns-policyserver-mapper](https://artifacthub.io/packages/kubewarden/kubewarden-policy-library/ns-policyserver-mapper) policy, their own policy or other means, such as GitOps.

See: https://docs.kubewarden.io/howtos/policy-servers/namespaced-policies-capabilities

### Workarounds

Cluster Operators can opt for:
- Not allowing users to create namespaced policies (AdmissionPolicies, AdmissionPolicyGroups).
- Removing SubjectAccessReview "create" permissions for the PolicyServer ServiceAccount RBAC being used, in custom PolicyServers and the  PolicyServer `default`.

### Resources

- Code changes, with new security feature: https://github.com/kubewarden/kubewarden-controller/pull/1693
- Documentation changes: https://github.com/kubewarden/docs/pull/737
  - Explained new feature on 1.35.0
  - Updated Threat model assessment

## References
- https://github.com/kubewarden/adm-controller/security/advisories/GHSA-wqcw-g35j-j578
- https://github.com/kubewarden/kubewarden-controller/security/advisories/GHSA-wqcw-g35j-j578
- https://nvd.nist.gov/vuln/detail/CVE-2026-42541
- https://github.com/kubewarden/docs/pull/737
- https://github.com/kubewarden/kubewarden-controller/pull/1693
- https://docs.kubewarden.io/howtos/policy-servers/namespaced-policies-capabilities
- https://github.com/kubewarden/kubewarden-controller
