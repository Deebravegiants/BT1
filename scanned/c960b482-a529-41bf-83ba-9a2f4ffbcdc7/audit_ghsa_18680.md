# [M] Rancher user retains access to clusters despite Global Role removal

## Summary
Severity: Medium
Advisory: GHSA-j4vr-pcmw-hx59
CVE: CVE-2023-32199
CWE: CWE-281
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2025-10-24
Source: https://github.com/advisories/GHSA-j4vr-pcmw-hx59
Type: github-advisory

## Affected
- Go: `github.com/rancher/rancher` — affected >=0 <0.0.0-20251014212116-7faa74a968c2

## Details
### Impact
A vulnerability has been identified within Rancher Manager, where after removing a custom GlobalRole that gives administrative access or the corresponding binding, the user still retains access to clusters.
This only affects custom Global Roles that:
- Have a `*` on `*` in `*` rule for resources
- Have a `*` on `*` rule for non-resource URLs

For example
```yaml
apiVersion: management.cattle.io/v3
kind: GlobalRole
metadata:
  name: custom-admin
rules:
  - apiGroups:
      - '*'
    resources:
      - '*'
    verbs:
      - '*'
  - nonResourceURLs:
      - '*'
    verbs:
      - '*'
```

Specifically:
- When a user is bound to a custom admin `GlobalRole`, a corresponding `ClusterRoleBinding` is created on all clusters that binds them to the cluster-admin `ClusterRole`.
- When such a `GlobalRole` or the `GlobalRoleBinding` (e.g., when the user is unassigned from this role in UI) is deleted, the `ClusterRoleBinding` that binds them to the cluster-admin ClusterRole stays behind.

This issue allows a user to continue having access to clusters after they have been unassigned from the custom admin global role or the role has been deleted.

Please consult the associated  [MITRE ATT&CK - Technique - Account Access Removal](https://attack.mitre.org/techniques/T1531/) for further information about this category of attack.

### Patches
This vulnerability is addressed by removing the corresponding `ClusterRoleBindings` whenever the admin `GlobalRole` or its `GlobalRoleBindings` are deleted. Previously orphaned `ClusterRoleBindings` are marked with the annotation `authz.cluster.cattle.io/admin-globalrole-missing=true` and should be deleted manually.

Orphaned ClusterRoleBindings can be listed with:
```
kubectl get clusterrolebinding -o jsonpath='{range .items[?(@.metadata.annotations.authz\.cluster\.cattle\.io/admin-globalrole-missing=="true")]}{.metadata.name}{"\n"}{end}'
```

Patched versions of Rancher include releases `v2.12.3`, `v2.11.7`.

Complications with the restricted admin functionality prevented the patches from being included in `v2.10` and `v2.9`.

### Workarounds
If the deployment can't be upgraded to a fixed version, users are advised to manually identify the orphaned `ClusterRoleBindings` and remove them.

### References
If you have any questions or comments about this advisory:
- Contact the [SUSE Rancher Security team](https://github.com/rancher/rancher/security/policy) for security related inquiries.
- Open an issue in the [Rancher](https://github.com/rancher/rancher/issues/new/choose) repository.
- Verify with our [support matrix](https://www.suse.com/suse-rancher/support-matrix/all-supported-versions/) and [product support lifecycle](https://www.suse.com/lifecycle/).

## References
- https://github.com/rancher/rancher/security/advisories/GHSA-j4vr-pcmw-hx59
- https://nvd.nist.gov/vuln/detail/CVE-2023-32199
- https://github.com/rancher/rancher/pull/52303
- https://bugzilla.suse.com/show_bug.cgi?id=CVE-2023-32199
- https://github.com/rancher/rancher
