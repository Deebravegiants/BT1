# [C] Kyverno's NamespacedGeneratingPolicy generator.apply() namespace argument unvalidated -- background controller creates RoleBindings in any namespace including kube-system

## Summary
Severity: Critical
Advisory: GHSA-79gf-7frw-68m9
CVE: CVE-2026-54523
CWE: CWE-862
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2026-08-26
Source: https://github.com/advisories/GHSA-79gf-7frw-68m9
Type: github-advisory

## Affected
- Go: `github.com/kyverno/kyverno` — affected >=1.18.0 <1.18.2

## Details
## Summary

In Kyverno v1.18.1, a tenant who can create a `NamespacedMutatingPolicy` in their own namespace can instruct the admission controller to generate resources in any namespace by passing an arbitrary namespace string to the CEL `generator.apply(namespace, resources)` function.

## Details

`pkg/cel/libs/context.go:177` declares `GenerateResources(namespace string, dataList []map[string]any)`. The `namespace` argument arrives unvalidated from the CEL expression `generator.apply("<target-namespace>", [...])`.

### Version-Specific Impact

**v1.18.0, v1.18.1 (affected via NamespacedMutatingPolicy only):**

The nmpol CEL compiler unintentionally exposes the `generator` library to match condition expressions. A namespaced mutating policy can invoke `generator.apply()` in a boolean CEL expression such as `matchConditions`, triggering the admission controller to generate resources in any namespace at request time. This side effect executes with the admission controller's cluster-wide privileges.

NamespacedGeneratingPolicy is **not** a vector in v1.18.1 due to incomplete webhook and background processing wiring (not registered or functional).

### Root Cause

The admission validator for `NamespacedMutatingPolicy` (`pkg/cel/policies/mpol/validate.go`) only checks that the policy compiles and does not enforce namespace scope on `generator.apply()` arguments.

Compare correctly-guarded equivalents: `pkg/engine/context/loaders/configmap.go:102` rejects cross-namespace ConfigMap references for namespaced policies, and `pkg/engine/apicall/apicall.go:73-82` enforces namespace segment matching. `GenerateResources` has neither guard.

## Proof of Concept

Prerequisites: namespace `tenant-ns` exists; attacker has `create` on `namespacedmutatingpolicies.policies.kyverno.io` in `tenant-ns`.

```yaml
apiVersion: policies.kyverno.io/v1beta1
kind: NamespacedMutatingPolicy
metadata:
  name: cross-ns-escalate
  namespace: tenant-ns
spec:
  matchConstraints:
    resourceRules:
    - apiGroups: [""]
      apiVersions: ["v1"]
      resources: ["configmaps"]
      operations: ["CREATE"]
  mutations:
  - patchType: applyConfiguration
    applyConfiguration:
      expression: object
  matchConditions:
  - name: trigger-escalation
    expression: |
      generator.apply("kube-system", [
        {
          "apiVersion": dyn("v1"),
          "kind": dyn("ConfigMap"),
          "metadata": dyn({
            "name": "kube-system-config",
            "namespace": "kube-system"
          }),
          "data": dyn({
            "injected-by": "tenant-policy",
            "impact": "unauthorized access to kube-system namespace"
          })
        }
      ])
```

Apply the policy, then create any ConfigMap in `tenant-ns` to trigger the admission webhook. The admission controller creates `configmap/kube-system-config` in `kube-system`. By default, the admission controller has `create` on ConfigMaps in all namespaces.

## Impact

A namespace-scoped user with `create` on `NamespacedMutatingPolicy` in >=v1.18.1 can create ConfigMaps, NetworkPolicies, Secrets, and other resources in any namespace using the admission controller's cluster-wide RBAC. This allows:

Injecting sensitive configuration into protected namespaces (e.g., `kube-system`, `default`)
Disrupting cluster networking via NetworkPolicies
Privilege escalation via RoleBinding creation (for roles the admission controller holds or lesser-privileged roles)
Privilege escalation via RoleBinding creation in other namespaces
Any installation that grants non-admin users access to `NamespacedMutatingPolicy` creation is affected.

## Timeline

* 2026-05-20: Vulnerability reproduced on main
* 2026-07-13: CVE-2026-54523 / GHSA-79gf-7frw-68m9 published
* 2026-07-22: Advisory clarified to document actual v1.18.1 attack vector (NamespacedMutatingPolicy in matchConditions, not NamespacedGeneratingPolicy)

## Advisory Update

This advisory was updated to clarify the v1.18.1 attack surface. The nmpol vector in matchConditions was the reachable attack path in v1.18.1, while ngpol lacked end-to-end plumbing. The CVE, patched version, and CVSS score remain unchanged. Original report by @0xVijay.

## References
- https://github.com/kyverno/kyverno/security/advisories/GHSA-79gf-7frw-68m9
- https://github.com/kyverno/kyverno/pull/16238
- https://github.com/kyverno/kyverno/commit/0919553c0ea1904f8d891280c92018da97946a06
- https://github.com/kyverno/kyverno/commit/5164bcdeda5b57678bc2d7a03ecc2cbb02982dae
- https://github.com/kyverno/sdk/commit/6573937441443e1ba5af9fbb28d5c0f20297f9df
- https://github.com/kyverno/kyverno
- https://github.com/kyverno/kyverno/releases/tag/v1.18.2
