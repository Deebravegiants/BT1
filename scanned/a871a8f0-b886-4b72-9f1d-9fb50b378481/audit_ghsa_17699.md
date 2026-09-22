# [M] KubeWarden's AdmissionPolicy and AdmissionPolicyGroup policies can be used to alter PolicyReport resources

## Summary
Severity: Medium
Advisory: GHSA-fc89-jghx-8pvg
CVE: CVE-2025-24376
CWE: CWE-155
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:L (CVSS_V3)
Published: 2025-01-30
Source: https://github.com/advisories/GHSA-fc89-jghx-8pvg
Type: github-advisory

## Affected
- Go: `github.com/kubewarden/kubewarden-controller` — affected >=1.7.0 <1.21.0

## Details
### Impact

By design, AdmissionPolicy and AdmissionPolicyGroup can evaluate only namespaced resources. The resources to be evaluated are determined by the rules provided by the user when defining the policy.
There might be Kubernetes namespaced resources that should not be validated by AdmissionPolicy and by the AdmissionPolicyGroup policies because of their sensitive nature.
For example, PolicyReport are namespaced resources that contain the list of non compliant objects found inside of a namespace. See [this section](https://docs.kubewarden.io/explanations/audit-scanner/policy-reports) of Kubewarden’s documentation for more details about PolicyReport resources.
An attacker can use either an AdmissionPolicy or an AdmissionPolicyGroup to prevent the creation and update of PolicyReport objects to hide non-compliant resources.
Moreover, the same attacker might use a mutating AdmissionPolicy to alter the contents of the PolicyReport created inside of the namespace.

### Patches

Starting from the 1.21.0 release, the validation rules applied to AdmissionPolicy and AdmissionPolicyGroup have been tightened to prevent them from validating sensitive types of namespaced resources.
The new validation will also restrict the usage of wildcards when defining apiGroups and resources rules for AdmissionPolicy and AdmissionPolicyGroup objects.

### Workarounds

On clusters running Kubewarden < 1.21.0, the following Kubewarden policy can be applied to prevent the creation of AdmissionPolicy and AdmissionPolicyGroup resources that interact with PolicyReport resources:

```yaml
apiVersion: policies.kubewarden.io/v1
kind: ClusterAdmissionPolicy
metadata:
  name: "deny-interaction-with-policyreport"
spec:
  module: registry://ghcr.io/kubewarden/policies/cel-policy:latest
  settings:
    variables:
      - name: hasWildcardInsideOfApiGroup
        expression: "object.spec.rules.exists(r, r.apiGroups.exists(ag, ag == '*'))"
      - name: hasWildcardInsideOfResources
        expression: "object.spec.rules.exists(r, r.resources.exists(ag, ag == '*' || ag == '*/*' || ag == 'policyreports/*'))"
      - name: dealsWithPolicyReportApiGroup
        expression: "object.spec.rules.exists(r, r.apiGroups.exists(ag, ag == 'wgpolicyk8s.io'))"
      - name: dealsWithPolicyReportResource
        expression: "object.spec.rules.exists(r, r.resources.exists(ag, ag == 'policyreports' || ag == 'policyreports/'))"
      - name: isPendingDeletion
        expression: "has(object.metadata.deletionTimestamp)"
    validations:
      - expression: |
          !( variables.hasWildcardInsideOfApiGroup ||
             variables.hasWildcardInsideOfResources ||
             variables.dealsWithPolicyReportResource ||
             variables.dealsWithPolicyReportApiGroup
          ) || variables.isPendingDeletion
        message: "cannot target PolicyReport resources or use wildcards in apiGroups or resources"
  rules:
    - apiGroups: ["policies.kubewarden.io"]
      apiVersions: ["v1"]
      operations: ["CREATE", "UPDATE"]
      resources: ["admissionpolicies", "admissionpolicygroups"]
  mutating: false
  backgroundAudit: true
```

### For more information

If you have any questions or comments about this advisory you can contact the Kubewarden team using the procedures described under the “[security disclosure](https://docs.kubewarden.io/disclosure)“ guidelines of the Kubewarden project.

## References
- https://github.com/kubewarden/kubewarden-controller/security/advisories/GHSA-fc89-jghx-8pvg
- https://nvd.nist.gov/vuln/detail/CVE-2025-24376
- https://github.com/kubewarden/kubewarden-controller/commit/8124039b5f0c955d0ee8c8ca12d4415282f02d2c
- https://github.com/kubewarden/kubewarden-controller
- https://pkg.go.dev/vuln/GO-2025-3434
