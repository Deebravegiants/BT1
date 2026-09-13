# [M] Traefik: Gateway HTTPRoute backendRef filters can leak backend context across routes sharing a Service:port

## Summary
Severity: Medium
Advisory: GHSA-6p8f-p8j2-rqmv
CVE: CVE-2026-54765
CWE: CWE-284, CWE-863
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:N/VA:N/SC:L/SI:H/SA:N (CVSS_V4)
Published: 2026-08-06
Source: https://github.com/advisories/GHSA-6p8f-p8j2-rqmv
Type: github-advisory

## Affected
- Go: `github.com/traefik/traefik/v3` — affected >=3.7.0 <3.7.6

## Details
## Summary

There is a medium severity vulnerability in Traefik's Kubernetes Gateway API provider.
When two accepted HTTPRoutes target the same backend Service:port but configure different
`backendRef` filters, Traefik may resolve both routes to the same child service and apply
only one route's filter set to all requests reaching that backend. In Gateway deployments
where `backendRef` filters set security-sensitive headers — such as tenant identity,
authorization context, or values the backend trusts — an attacker who can create an
accepted HTTPRoute sharing the same backend Service:port may cause their route's filter
context to be applied to another route's requests, potentially crossing namespace
boundaries when a `ReferenceGrant` permits cross-namespace targeting.

## Patches

- https://github.com/traefik/traefik/releases/tag/v3.7.6

## For more information

If you have any questions or comments about this advisory, please [open an issue](https://github.com/traefik/traefik/issues).

<details>
<summary>Original Description</summary>

# Traefik Gateway HTTPRoute backendRef filter context collision across routes sharing Service:port

## Summary

Traefik's Kubernetes Gateway API provider builds the dynamic HTTP backend service key for a Gateway `HTTPRoute` backendRef from only the backend namespace, Service name, protocol, and port. It does not include the HTTPRoute, listener, rule, or backendRef filter identity in that key.

When two accepted HTTPRoutes point to the same backend `Service:port` but define different backendRef filters, Traefik can make both route WRR services reference the same child service. The child service then carries only one backendRef filter set, so one route can send requests to the backend with another route's backend context.

This is security-relevant when backendRef filters set, remove, or rewrite security-sensitive context, such as tenant, identity, auth, sanitization, Host, or path headers trusted by the backend.

Credit: Qican Ma, Ding Luo @XiaoMi ShadowBlade Security Lab

## Suggested Severity

Suggested severity: Medium/High, configuration-dependent.

Suggested CVSS 3.1:

```text
CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:L/I:H/A:N
```

Notes:

- Requires Gateway API routes sharing the same backend Service:port with different security-sensitive backendRef filters trusted by the backend.
- Cross-namespace impact is possible when route attachment and ReferenceGrant policy allow an attacker route to target the shared backend.
- No RCE, memory corruption, or default-config exposure claimed.

Suggested CWE:

```text
CWE-863: Incorrect Authorization
CWE-284: Improper Access Control
```

## Affected Component

```text
pkg/provider/kubernetes/gateway/httproute.go — loadService(), loadMiddlewares()
```

## Tested Versions

Confirmed on:

```text
Traefik source snapshot: 29406d42898547f1ffabd904f66af06c212740cf on master
```

Earliest affected version not exhaustively determined.

## Root Cause

`loadService` starts the dynamic service name from backend namespace and Service name only:

```go
// pkg/provider/kubernetes/gateway/httproute.go:245
serviceName := provider.Normalize(namespace + "-" + string(backendRef.Name) + "-http")
```

It loads backendRef filters using that same service name before appending the backend port:

```go
// pkg/provider/kubernetes/gateway/httproute.go:258
middlewares, err := p.loadMiddlewares(conf, namespace, serviceName, backendRef.Filters, pathMatch)
```

For normal Kubernetes Services, the final child service key appends only the port:

```go
// pkg/provider/kubernetes/gateway/httproute.go:304-317
portStr := strconv.FormatInt(int64(port), 10)
serviceName = provider.Normalize(serviceName + "-" + portStr)
...
conf.HTTP.Services[serviceName] = &dynamic.Service{LoadBalancer: lb, Middlewares: middlewares}
```

Each route/rule WRR service references the child service by name. Later route configs are merged by map key (`maps.Copy`), so both route-local WRR services can point to the same child service, which retains only one of the route/backendRef filter configurations.

## Attack Scenario

1. Gateway listener with `allowedRoutes.namespaces.from: All`.
2. Victim `HTTPRoute` `route-a` in namespace `default` targets `default/whoami:80` with backendRef filter setting `X-Tenant: tenant-a`.
3. Attacker-controlled `HTTPRoute` `route-b` in namespace `attacker` targets `default/whoami:80` (via ReferenceGrant) with backendRef filter setting `X-Tenant: tenant-b`.
4. Both routes generate the same child service key: `default-whoami-http-80`.
5. The second route's filter configuration overwrites the first (or vice versa) via `maps.Copy`.
6. Backend receives both routes' requests with one tenant's header context.

## Proof of Concept

A Go test harness injects provider-level and server-level tests into the Traefik checkout. The provider test confirms the generated dynamic configuration collision. The server test builds Traefik's runtime router/service/middleware pipeline and sends `httptest` requests through router matching, WRR service dispatch, service-level backendRef middleware, and backend proxy capture.

Observed result:

```json
{
  "name": "positive_cross_namespace_same_backend_filter_collision",
  "pass": true,
  "expected": {"route-a": "tenant-a", "route-b": "tenant-b"},
  "observed": {"route-a": "tenant-a", "route-b": "tenant-a"},
  "runtimeObserved": {"route-a": "tenant-a", "route-b": "tenant-a"},
  "childServices": {"route-a": "default-whoami-http-80", "route-b": "default-whoami-http-80"}
}
```

Negative controls confirmed:

- Separate backend Service:port keys produce correct per-route filter isolation.
- Identical filters across routes produce no security-relevant difference.

The PoC files can be shared upon request.

## Impact

An actor who can create or modify an accepted HTTPRoute can cause another accepted route that targets the same backend Service:port to use the wrong backendRef filter context. In cross-namespace Gateway deployments, this can cross namespace boundaries.

High-value impact: gateway-injected tenant, identity, auth, role, header sanitization, Host rewrite, or path rewrite context is trusted by the backend.
Lower-value impact: the overwritten header is informational or observability-only.

## Suggested Remediation

1. Include route/listener/rule/backendRef filter identity in the generated child service name when backendRef filters are present.
2. Split the load-balancer service from the backendRef filter application so per-route backend filters remain route-scoped.
3. Detect conflicting backendRef filters for the same generated service key and reject or disambiguate the configuration.

## Timeline

```text
2026-06-04: Discovered and reproduced with local test harness.
```

</details>

---

## References
- https://github.com/traefik/traefik/security/advisories/GHSA-6p8f-p8j2-rqmv
- https://nvd.nist.gov/vuln/detail/CVE-2026-54765
- https://github.com/traefik/traefik/pull/13367
- https://github.com/traefik/traefik/commit/8aada7a7d52e4588a75386d8b86d270f6fe8d549
- https://github.com/traefik/traefik
- https://github.com/traefik/traefik/releases/tag/v3.7.6
