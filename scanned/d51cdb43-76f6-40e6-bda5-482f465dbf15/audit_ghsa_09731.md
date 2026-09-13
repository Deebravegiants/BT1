# [M] Traefik Kubernetes CRD allows unauthorized cross-namespace middleware binding

## Summary
Severity: Medium
Advisory: GHSA-xhjw-95fp-8vgq
CVE: CVE-2026-41174
CWE: CWE-653, CWE-863
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-04-24
Source: https://github.com/advisories/GHSA-xhjw-95fp-8vgq
Type: github-advisory

## Affected
- Go: `github.com/traefik/traefik/v3` — affected >=3.7.0-ea.1 <3.7.0-rc.2
- Go: `github.com/traefik/traefik/v3` — affected >=3.0.0-beta1 <3.6.14
- Go: `github.com/traefik/traefik/v2` — affected >=0 <2.11.43
- Go: `github.com/traefik/traefik` — affected >=0

## Details
## Summary

There is a vulnerability in Traefik's Kubernetes CRD provider cross-namespace isolation enforcement.

When `providers.kubernetesCRD.allowCrossNamespace=false`, Traefik correctly rejects direct cross-namespace middleware references from `IngressRoute` objects, but fails to apply the same restriction to middleware references nested inside a `Chain` middleware's `spec.chain.middlewares[]`. An actor with permission to create or update Traefik CRDs in their own namespace can exploit this to cause Traefik to resolve and apply middleware objects from another namespace, bypassing the documented isolation boundary.

## Patches

- https://github.com/traefik/traefik/releases/tag/v2.11.43
- https://github.com/traefik/traefik/releases/tag/v3.6.14
- https://github.com/traefik/traefik/releases/tag/v3.7.0-rc.2

## For more information

If there are any questions or comments about this advisory, please [open an issue](https://github.com/traefik/traefik/issues).

<details>
<summary>Original Description</summary>

### Summary
When `providers.kubernetesCRD.allowCrossNamespace=false`, Traefik still allows a namespace-local `Middleware` of type `Chain` to reference middleware objects from another namespace via `spec.chain.middlewares[].namespace`.

This bypasses the documented cross-namespace restriction and allows an actor with permission to create or update Traefik CRDs in namespace A to bind middleware defined in namespace B to routes in namespace A.

### Details
Traefik documents `allowCrossNamespace` as the control that governs whether `IngressRoute` objects may reference resources in other namespaces.

Direct middleware references from `IngressRoute.routes[].middlewares[]` are validated in `pkg/provider/kubernetes/crd/kubernetes_http.go` by `makeMiddlewareKeys(...)`, which rejects cross-namespace references when `allowCrossNamespace` is disabled.

However, nested middleware references inside `Middleware.spec.chain.middlewares[]` follow a different code path. `createChainMiddleware(...)` in `pkg/provider/kubernetes/crd/kubernetes.go` does not receive or enforce `allowCrossNamespace`; it resolves `mi.Namespace` (or defaults to the current namespace) and appends `makeID(ns, mi.Name)` unconditionally.

At runtime, `pkg/server/middleware/middlewares.go` qualifies and builds `config.Chain.Middlewares`, so the cross-namespace middleware is actually loaded and used.

This was verified on the current `master` at commit `786f7192e11878dfaa634f8263bf79bb730a71cb`.

This appears related to earlier cross-namespace hardening work, but the surviving issue is a distinct nested `Chain` middleware code path rather than the already-guarded direct reference path.

### Expected behavior
When `providers.kubernetesCRD.allowCrossNamespace=false`, any middleware reference that resolves to an object in another namespace should be rejected, whether referenced directly from an `IngressRoute` or indirectly through a local `Chain` middleware.

### Actual behavior
A namespace-local `Chain` middleware can reference `spec.chain.middlewares[].namespace` in another namespace, and Traefik resolves and applies that middleware even when cross-namespace references are disabled.

### Attacker prerequisites
The attacker must have permission to create or update Traefik CRDs in a namespace they control, but does not need permission to modify resources in the target namespace.

### PoC
1. Run Traefik with the Kubernetes CRD provider and set `allowCrossNamespace: false`.

2. Create two namespaces, for example `default` and `cross-ns`.

3. Apply a middleware in `cross-ns`:

```yaml
apiVersion: traefik.io/v1alpha1
kind: Middleware
metadata:
  name: victim-strip
  namespace: cross-ns
spec:
  stripPrefix:
    prefixes:
      - /secret
```

4. Apply a chain middleware in `default` that references the middleware above:

```yaml
apiVersion: traefik.io/v1alpha1
kind: Middleware
metadata:
  name: mychain
  namespace: default
spec:
  chain:
    middlewares:
      - name: victim-strip
        namespace: cross-ns
```

5. Apply an `IngressRoute` in `default` that references only the local `mychain` middleware:

```yaml
apiVersion: traefik.io/v1alpha1
kind: IngressRoute
metadata:
  name: demo
  namespace: default
spec:
  entryPoints:
    - web
  routes:
    - match: Host(`example.test`) && PathPrefix(`/demo`)
      kind: Rule
      middlewares:
        - name: mychain
      services:
        - name: whoami
          port: 80
```

6. Observe that Traefik accepts the configuration and resolves the resulting chain to the middleware from `cross-ns` even though `allowCrossNamespace` is disabled.

7. As a control, replace the local chain reference in the `IngressRoute` with a direct cross-namespace middleware reference. That direct reference is rejected when `allowCrossNamespace=false`, which indicates the bypass is specific to nested `Chain` middleware resolution.

### Impact

This is an authorization / trust-boundary bypass in Traefik's Kubernetes CRD provider.

Clusters that rely on providers.kubernetesCRD.allowCrossNamespace=false for namespace isolation are affected. An actor who is allowed to create or update Traefik CRDs in their own namespace can still cause Traefik to apply middleware from another namespace by referencing it indirectly through a local Chain middleware.

The practical impact depends on which middleware objects exist in the other namespace, but this can allow unauthorized reuse of security-sensitive or policy-bearing middleware across namespace boundaries. Examples include request modification, header manipulation, authentication or forward-auth related behavior, and other traffic-handling policies that were intended to remain namespace-scoped.

Testers have not verified unauthenticated remote compromise, code execution, or universal cross-tenant data exposure. The core issue is that a documented isolation control can be bypassed through the nested Chain middleware reference path.

</details>

## References
- https://github.com/traefik/traefik/security/advisories/GHSA-xhjw-95fp-8vgq
- https://nvd.nist.gov/vuln/detail/CVE-2026-41174
- https://github.com/traefik/traefik/commit/df00d82fc7f12e07199551832b54de6d0e55414d
- https://github.com/traefik/traefik
- https://github.com/traefik/traefik/releases/tag/v2.11.43
- https://github.com/traefik/traefik/releases/tag/v3.6.14
- https://github.com/traefik/traefik/releases/tag/v3.7.0-rc.2
