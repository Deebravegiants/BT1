# [M] Skipper's routesrv-no-auth component: All routesrv API Endpoints Lack Authentication

## Summary
Severity: Medium
Advisory: GHSA-5587-2x54-jj6h
CVE: CVE-2026-54246
CWE: CWE-306
Ecosystem: Go
CVSS: CVSS:3.1/AV:A/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-07-17
Source: https://github.com/advisories/GHSA-5587-2x54-jj6h
Type: github-advisory

## Affected
- Go: `github.com/zalando/skipper` — affected >=0 <0.27.13

## Details
## Description

The `routesrv` component exposes the full cluster route topology (Ingress/RouteGroup configurations, backend URLs, filter chains, OAuth/OIDC callback paths) and cache-cluster topology (Redis/Valkey shard addresses) over plain HTTP with **zero authentication**. Any pod in the Kubernetes cluster can reach routesrv via its predictable DNS name and retrieve sensitive cluster-wide routing and cache infrastructure data.

## Vulnerable Code

**routesrv/routesrv.go:87-99,114-137** — all handler registrations on the main mux:
```go
mux.Handle("/routes", b)          // eskipBytes.ServeHTTP — all route data
mux.Handle("/routes/{zone}", b)   // zone-scoped route data
mux.Handle("/swarm/redis/shards", rh)   // Redis cluster addresses
mux.Handle("/swarm/valkey/shards", vh)  // Valkey cluster addresses
```

**routesrv/eskipbytes.go:134-196** — `eskipBytes.ServeHTTP`:
```go
func (e *eskipBytes) ServeHTTP(rw http.ResponseWriter, r *http.Request) {
    // ... only checks GET/HEAD method, NO auth check
    if r.Method != "GET" && r.Method != "HEAD" {
        w.WriteHeader(http.StatusMethodNotAllowed)
        return
    }
    // ... serves all route data immediately
}
```

**routesrv/redishandler.go:28-41** — `RedisHandler.ServeHTTP`:
```go
func (rh *RedisHandler) ServeHTTP(w http.ResponseWriter, r *http.Request) {
    if r.Method != "GET" {
        w.WriteHeader(http.StatusMethodNotAllowed)
        return
    }
    // ... serves Redis cluster addresses immediately, NO auth check
}
```

**routesrv/valkeyhandler.go:28-41** — `ValkeyHandler.ServeHTTP`:
```go
func (vh *ValkeyHandler) ServeHTTP(w http.ResponseWriter, r *http.Request) {
    if r.Method != "GET" {
        w.WriteHeader(http.StatusMethodNotAllowed)
        return
    }
    // ... serves Valkey cluster addresses immediately, NO auth check
}
```

## Attack Path

1. **Initial Compromise**: Attacker compromises any pod in the Kubernetes cluster (via application CVE, supply-chain attack, malicious container image, etc.)
2. **Discovery**: Attacker discovers routesrv via predictable Kubernetes DNS name: `skipper-ingress-routesrv.kube-system.svc.cluster.local:9090` (documented at `docs/tutorials/operations.md:108`, `docs/tutorials/ratelimit.md:137,197`)
3. **Data Extraction without Auth**: 
   - `GET http://<routesrv>:9090/routes` → All Ingress/RouteGroup configurations across ALL namespaces
   - `GET http://<routesrv>:9090/swarm/redis/shards` → Redis cache cluster node addresses
   - `GET http://<routesrv>:9090/swarm/valkey/shards` → Valkey cache cluster node addresses
4. **Subsequent Attacks**: With cache cluster topology, attacker can perform direct cache-level attacks (ratelimit data manipulation, session data exfiltration)

## Permission Boundary Analysis

The routesrv uses a ServiceAccount with **cluster-wide RBAC** to list Ingress (networking.k8s.io), RouteGroup (zalando.org), Endpoints, and Services across all namespaces (see `clusterclient.go:648-653` `fetchClusterState`). The kube-apiserver requires proper ServiceAccount token + RBAC authorization for the Kubernetes API itself, but **routesrv exposes the aggregated data over HTTP with zero authentication**.

A compromised pod with limited RBAC (restricted to its own namespace) can bypass Kubernetes RBAC entirely by reading routesrv. This crosses the boundary from *"namespace-scoped Kubernetes workload with restricted RBAC"* to *"full cluster route topology across all namespaces"*.

No NetworkPolicy manifests exist in the `deploy/` directory. The default Kubernetes flat network model allows any pod to reach any service, further widening the attack surface.

## Exposed Data

| Endpoint | Data Exposed | Impact |
|----------|-------------|--------|
| `GET /routes` | All ingress/routegroup backends: internal service URLs, filter chains (auth, rate limiting, OAuth, JWT, OPA policies), load balancer group membership | Cluster-wide reconnaissance, targeted backend attacks |
| `GET /routes/{zone}` | Zone-scoped subset of above route data | Same, scoped |
| `GET /swarm/redis/shards` | Redis cluster internal IP:port pairs | Direct cache-level attacks, ratelimit data manipulation |
| `GET /swarm/valkey/shards` | Valkey cluster internal IP:port pairs | Same |

Additionally, the data-plane client (`eskipfile/remote.go:190-219`) also performs plain HTTP GET with no credentials — only an ETag header is sent — confirming that no auth capability exists in the architecture at all.


## Mitigation

1. Add authentication to all routesrv HTTP endpoints (basic auth, bearer token, mTLS, or shared secret) via flag `-route-server-filters=""`
2. Deploy Kubernetes NetworkPolicies restricting ingress to routesrv to only the data-plane skipper pod selectors
3. Consider using mutual TLS authentication between data-plane and control-plane components


### NetworkPolicy does not remove the missing-auth condition
Restrictive NetworkPolicies are a valid mitigation, but they are not an application-layer authentication mechanism. The security-relevant defect remains that routesrv serves control-plane-derived data to unauthenticated callers whenever network reachability exists.

### Impact framing
This report does **not** rely on claiming direct integrity or availability impact. The verified issue is a confidentiality-focused control-plane exposure: route definitions, backend topology, filter-chain details, and Redis/Valkey shard addresses become readable to any reachable in-cluster client.

## Resources

- `routesrv/routesrv.go:87-99` — handler registration (zero auth)
- `routesrv/eskipbytes.go:134-196` — route data handler (no auth)
- `routesrv/redishandler.go:28-41` — Redis shard handler (no auth)
- `routesrv/valkeyhandler.go:28-41` — Valkey shard handler (no auth)
- `dataclients/kubernetes/clusterclient.go:648-653` — `fetchClusterState()` — shows cluster-wide RBAC
- `eskipfile/remote.go:190-219` — data-plane client also has no auth capability
- `docs/tutorials/operations.md:108`, `docs/tutorials/ratelimit.md:137,197` — documented routesrv DNS name

## References
- https://github.com/zalando/skipper/security/advisories/GHSA-5587-2x54-jj6h
- https://github.com/zalando/skipper
- https://github.com/zalando/skipper/releases/tag/v0.27.13
