# [M] Traefik: Gateway API TraefikService backend accepts rest@internal, allowing unauthorized exposure of the REST provider despite providers.rest.insecure=false

## Summary
Severity: Medium
Advisory: GHSA-96qj-4jj5-wcjc
CVE: CVE-2026-44774
CWE: CWE-284
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:N/VA:N/SC:L/SI:H/SA:H (CVSS_V4)
Published: 2026-05-13
Source: https://github.com/advisories/GHSA-96qj-4jj5-wcjc
Type: github-advisory

## Affected
- Go: `github.com/traefik/traefik/v3` — affected >=3.7.0 <3.7.1
- Go: `github.com/traefik/traefik/v3` — affected >=0 <3.6.17
- Go: `github.com/traefik/traefik/v2` — affected >=0 <2.11.46
- Go: `github.com/traefik/traefik` — affected >=0

## Details
## Summary

There is a medium severity vulnerability in Traefik's Kubernetes Gateway API provider that allows a tenant with `HTTPRoute` creation permissions to expose the REST provider handler, bypassing the `providers.rest.insecure=false` setting. The Gateway provider accepts any `TraefikService` backend reference whose name ends with `@internal`, making it possible to route traffic to `rest@internal` in addition to the intended `api@internal`. In shared Gateway deployments where the REST provider is enabled, this allows a low-privileged actor to gain live dynamic configuration write access to Traefik, enabling unauthorized reconfiguration of routers and services.

## Patches

- https://github.com/traefik/traefik/releases/tag/v2.11.46
- https://github.com/traefik/traefik/releases/tag/v3.6.17
- https://github.com/traefik/traefik/releases/tag/v3.7.1

## For more information

If you have any questions or comments about this advisory, please [open an issue](https://github.com/traefik/traefik/issues).

<details>
<summary>Original Description</summary>

### Summary
When the Kubernetes Gateway API provider is enabled, Traefik accepts any `TraefikService` backend whose name ends with `@internal`. This allows a tenant-controlled `HTTPRoute` to publish `rest@internal`.

If `providers.rest` is enabled, this exposes Traefik's REST provider handler even when `providers.rest.insecure=false`, even though providers.rest.insecure=false is meant to keep the REST handler from being exposed by Traefik's built-in internal router. In a shared Gateway deployment, an actor with permission to create or update `HTTPRoute` resources in an allowed namespace can gain live Traefik dynamic-configuration write access through `PUT /api/providers/rest`.

### Details
The Gateway provider treats internal services broadly rather than allowing only a specific internal target.

In current `master`, `pkg/provider/kubernetes/gateway/kubernetes.go` defines `isInternalService(...)` as any `TraefikService` reference whose name ends with `@internal`.

Then `pkg/provider/kubernetes/gateway/httproute.go` special-cases a single backend reference that matches `isInternalService(...)` and directly assigns `router.Service = string(routeRule.BackendRefs[0].Name)`.

This means a tenant route can target not only `api@internal`, but also `rest@internal` and other internal handlers.

Separately, the REST provider handler is created whenever the REST provider is enabled. In `pkg/server/service/managerfactory.go`, if `staticConfiguration.Providers.Rest != nil`, Traefik sets `factory.restHandler = staticConfiguration.Providers.Rest.CreateRouter()`.

The REST provider handler itself is implemented in `pkg/provider/rest/rest.go` and accepts `PUT /api/providers/{provider}`.

The `providers.rest.insecure` flag does not disable the underlying handler. In `pkg/provider/traefik/internal.go`, that flag only controls whether Traefik creates its own built-in internal router for `rest@internal`. Even when `providers.rest.insecure=false`, Traefik still registers the `rest` service object, and the service layer can still resolve `rest@internal` if another provider routes to it.

I validated this locally in two tests:
1. the Gateway route-building path accepts `rest@internal` as an internal backend through the same special-case branch used for `api@internal`
2. the service layer builds and serves `rest@internal` successfully when `providers.rest` is enabled and `providers.rest.insecure=false`

The vulnerable code path is present in:
- `v3.0.0`
- `v3.6.7`
- `v2.11.0`
- `v2.11.36`
- current `master` at `786f7192e11878dfaa634f8263bf79bb730a71cb`

I verified the issue in v3.0.0, v3.6.7, v2.11.0, v2.11.36, and current master; the reported affected ranges reflect the maintained release lines checked during validation

I did not find a public Traefik advisory or CVE for this exact issue. The closest public overlap I found is the documented/tested Gateway support for `api@internal`, but the issue here is broader because the Gateway code accepts any `@internal` `TraefikService`, including the write-capable `rest@internal` handler.

### Expected behavior
`providers.rest.insecure=false` should prevent low-privileged route authors from exposing the REST provider handler.

### Actual behavior
A tenant-controlled Gateway route can still publish `rest@internal` and reach the REST update API.

### Attacker prerequisites
- The Kubernetes Gateway API provider is enabled.
- `providers.rest=true`.
- `providers.rest.insecure=false`.
- A shared Gateway allows tenant namespaces to attach `HTTPRoute` resources.
- The attacker can create or update `HTTPRoute` resources in an allowed tenant namespace.

### PoC
1. Configure Traefik so that the Kubernetes Gateway provider is enabled, the REST provider is enabled, and the REST provider is not exposed insecurely.

Example static configuration:

```yaml
providers:
  kubernetesGateway: {}
  rest:
    insecure: false
```

2. Ensure a shared Gateway allows tenant `HTTPRoute` attachment.

3. In an allowed tenant namespace, create an `HTTPRoute` whose backend points to `rest@internal`:

```yaml
apiVersion: gateway.networking.k8s.io/v1
kind: HTTPRoute
metadata:
  name: expose-rest-internal
  namespace: tenant-a
spec:
  parentRefs:
    - name: shared-gateway
      namespace: infra
  hostnames:
    - rest.tenant.example
  rules:
    - matches:
        - path:
            type: PathPrefix
            value: /
      backendRefs:
        - group: traefik.io
          kind: TraefikService
          name: rest@internal
          port: 80
```

4. Send a `PUT` request through that published route to `/api/providers/rest` with a valid dynamic configuration body. A harmless proof can add a dummy router pointing to `noop@internal`.

Example request body:

```json
{
  "http": {
    "routers": {
      "probe": {
        "rule": "PathPrefix(`/probe`)",
        "service": "noop@internal",
        "ruleSyntax": "default"
      }
    }
  }
}
```

5. Observe that Traefik accepts the update and applies the supplied dynamic configuration, even though `providers.rest.insecure=false`.

### Impact
This is an authorization / trust-boundary bypass affecting shared Gateway deployments.

On affected deployments, an actor who should only be able to create or update `HTTPRoute` objects can escalate to live Traefik dynamic-configuration write access. That can allow unauthorized reconfiguration of routers and services, publication of additional internal surfaces, request interception or rerouting, and denial of service through destructive config changes.

On affected deployments, this gives a low-privileged Gateway route author live Traefik dynamic-configuration write access. This is critical for affected shared Gateway deployments because it can give a low-privileged route author live Traefik dynamic-configuration write access, but it depends on providers.rest being enabled.

This is not an unauthenticated vulnerability in all Traefik deployments. The issue depends on realistic but specific conditions:
- `providers.rest` must be enabled
- the attacker must be allowed to attach `HTTPRoute` resources to a shared Gateway

</details>

## References
- https://github.com/traefik/traefik/security/advisories/GHSA-96qj-4jj5-wcjc
- https://nvd.nist.gov/vuln/detail/CVE-2026-44774
- https://github.com/traefik/traefik
- https://github.com/traefik/traefik/releases/tag/v2.11.46
- https://github.com/traefik/traefik/releases/tag/v3.6.17
- https://github.com/traefik/traefik/releases/tag/v3.7.1
