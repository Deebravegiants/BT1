# [M] kubernetes-graphql-gateway: GraphQL Endpoint Vulnerable to Authenticated Denial-of-Service via Unrestricted Query Execution

## Summary
Severity: Medium
Advisory: GHSA-h9mw-h4qc-f5jf
CWE: CWE-400, CWE-770
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-04-08
Source: https://github.com/advisories/GHSA-h9mw-h4qc-f5jf
Type: github-advisory

## Affected
- Go: `github.com/platform-mesh/kubernetes-graphql-gateway` — affected >=0 <1.2.9

## Details
**CVSS 6.5 Medium** — The GraphQL API served by kubernetes-graphql-gateway is vulnerable to Denial-of-Service (DoS) attacks due to a complete absence of query resource controls (depth limiting, complexity analysis, response size capping, and rate limiting). An authenticated attacker can craft queries that force the server to compute and serialize multi-megabyte responses, consuming significant CPU, memory, and network bandwidth. Repeated requests can exhaust server resources and degrade or deny service to legitimate users.

> **Note:** A previous version of this advisory (based on pre-v1 code) documented an unauthenticated attack surface via an HTTP GET method bypass in the former `registry.go`. That bypass has been removed in v1 — all requests now require a Bearer token. The CVSS score has been adjusted from 7.5 to 6.5 accordingly (Privileges Required: None → Low). CWE-306 (Missing Authentication for Critical Function) no longer applies.

## Root Cause

The kubernetes-graphql-gateway uses the `graphql-go/graphql` library (v0.8.1) with the `graphql-go/handler` HTTP handler. The handler is instantiated in `gateway/gateway/graphql/graphql.go` with only cosmetic configuration — no resource limits:

```go
// gateway/gateway/graphql/graphql.go — CreateHandler()
func (s *GraphQLServer) CreateHandler(schema *graphql.Schema) *GraphQLHandler {
    graphqlHandler := handler.New(&handler.Config{
        Schema:     schema,
        Pretty:     s.config.Pretty,
        Playground: s.config.Playground,
        GraphiQL:   s.config.GraphiQL,
    })
    return &GraphQLHandler{
        Schema:  schema,
        Handler: graphqlHandler,
    }
}
```

The `handler.Config` struct does not include `MaxDepth`, `MaxComplexity`, `MaxResponseSize`, or any equivalent fields. Neither the `graphql-go/handler` nor the underlying `graphql-go/graphql` library provides built-in query depth or complexity analysis.

The application configuration (`gateway/gateway/config/config.go`) has no fields for resource limits:

```go
// gateway/gateway/config/config.go — GraphQL config
type GraphQL struct {
    Pretty     bool
    Playground bool
    GraphiQL   bool
}
```

No rate limiting, throttling, or request size controls exist anywhere in the codebase.

## Authentication Model

All requests pass through the HTTP handler in `gateway/http/http.go`, which extracts a Bearer token and injects it into the request context:

```go
// gateway/http/http.go — Token extraction (applied to all methods)
s.Handle("/api/clusters/{clusterName}", http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
    clusterName := r.PathValue("clusterName")
    authHeader := r.Header.Get("Authorization")
    token := strings.TrimPrefix(authHeader, "Bearer ")
    ctx := utilscontext.SetToken(r.Context(), token)
    ctx = utilscontext.SetCluster(ctx, clusterName)
    c.Gateway.ServeHTTP(w, r.WithContext(ctx))
}))
```

The token is enforced at the Kubernetes API layer via `gateway/gateway/roundtripper/bearer.go`, which returns HTTP 401 for requests without a valid token. However, the GraphQL execution engine (query parsing, schema validation, introspection) still runs **before** the Kubernetes API is contacted — meaning authenticated users can trigger expensive operations that consume server resources without hitting the K8s API at all.

## Attack Vectors

### 1. Nested Introspection Field Expansion

The GraphQL schema contains 3,508 types (Kubernetes resources + platform CRDs). Introspection meta-fields (`__schema`, `__type`) allow recursive field expansion. Each additional nesting level multiplies the response size exponentially. A single full introspection query generates ~5.2 MB of response data in ~1.15s.

### 2. Parallel Request Amplification

Without rate limiting, an authenticated attacker can issue many concurrent expensive queries. 5 parallel requests generate ~18.6 MB total response in under 4 seconds with no throttling. At scale (e.g. 999 concurrent requests), the backend becomes unresponsive and returns 503 to all users.

### 3. Subscription Resource Exhaustion

The `HandleSubscription()` method in `gateway/gateway/graphql/graphql.go` processes SSE (Server-Sent Events) subscription requests. A malicious authenticated client can open many subscription channels simultaneously, holding server connections and memory indefinitely:

```go
// gateway/gateway/graphql/graphql.go — HandleSubscription()
subscriptionChannel := graphql.Subscribe(subscriptionParams)
for res := range subscriptionChannel {
    // ... marshal and flush indefinitely ...
}
```

There is no limit on the number of concurrent subscriptions, no idle timeout, and no per-client connection cap.

### 4. Deep Query Execution

Authenticated users can submit arbitrarily deep and complex GraphQL queries. The GraphQL execution engine processes the full query — consuming CPU and memory for schema validation, field resolution, and error/response formatting — before any Kubernetes API authorization is checked. The request handling in `gateway/gateway/endpoint/endpoint.go` passes directly to the handler with no query guards:

```go
// gateway/gateway/endpoint/endpoint.go — ServeHTTP()
func (e *Endpoint) ServeHTTP(w http.ResponseWriter, r *http.Request) {
    if e.handler == nil || e.handler.Handler == nil {
        http.Error(w, "Endpoint not ready", http.StatusServiceUnavailable)
        return
    }
    if r.Header.Get("Accept") == "text/event-stream" {
        e.graphqlServer.HandleSubscription(w, r, e.handler.Schema)
        return
    }
    e.handler.Handler.ServeHTTP(w, r)
}
```

## Impact

- **Availability (High):** Service denial achievable — concurrent expensive queries cause backend to become unresponsive (503 for all users). With 3,508 types and no depth limits, each introspection query generates a ~5.2 MB response. The absence of rate limiting, query complexity controls, and response size caps allows an authenticated attacker to exhaust server CPU, memory, and bandwidth.
- **Confidentiality (None):** Information disclosure is covered in a separate finding.
- **Integrity (None):** No data modification possible.

## Affected Components

- `gateway/gateway/graphql/graphql.go` — Handler creation with no resource limits; subscription handler with no connection limits
- `gateway/gateway/endpoint/endpoint.go` — Direct passthrough to handler, no query depth/complexity middleware
- `gateway/gateway/config/config.go` — No configuration fields for resource limits
- `gateway/http/http.go` — No rate limiting middleware
- `graphql-go/graphql` library — No built-in depth/complexity limiting
- `graphql-go/handler` — No resource limit configuration options

## Recommendations

1. **Disable Introspection in Production** — As a defense-in-depth measure, disable introspection in non-development environments. This removes the highest-cost query path. If GraphiQL/Playground must remain accessible for development, gate it behind an environment flag.
2. **Implement Query Depth and Complexity Limiting** — Implement middleware that parses the query AST and rejects queries exceeding configurable thresholds before execution. Recommended maximum depth: 10 levels. Assign cost values to fields and enforce a maximum query cost budget — introspection meta-fields (`__schema`, `__type`) should carry elevated costs. Alternatively, consider migrating to a GraphQL library with built-in depth/complexity support (e.g., `gqlgen` with its complexity extension, or `graph-gophers/graphql-go` with its `MaxDepth` option).
3. **Implement Rate Limiting and Response Size Controls** — Add per-user rate limiting on the GraphQL endpoint. Suggested thresholds: 60 requests/minute for authenticated users, 2 requests/minute for introspection queries. Cap response payload size (e.g., 5 MB). For subscriptions, enforce maximum concurrent connections per client, idle timeouts, and maximum subscription duration.
4. **Add Resource Limit Configuration** — Extend the `GraphQL` struct in `gateway/gateway/config/config.go` to expose all resource limits (max query depth, max complexity, max response size, rate limit thresholds) as configurable parameters. This ensures all protective thresholds can be tuned per environment without code changes.

## References

- [OWASP GraphQL Cheat Sheet — Resource Limits](https://cheatsheetseries.owasp.org/cheatsheets/GraphQL_Cheat_Sheet.html)
- [OWASP API4:2023 — Unrestricted Resource Consumption](https://owasp.org/API-Security/editions/2023/en/0xa4-unrestricted-resource-consumption/)
- [CWE-770: Allocation of Resources Without Limits or Throttling](https://cwe.mitre.org/data/definitions/770.html)
- [CWE-400: Uncontrolled Resource Consumption](https://cwe.mitre.org/data/definitions/400.html)

## Classification

- **CWE-770** — Allocation of Resources Without Limits or Throttling
- **CWE-400** — Uncontrolled Resource Consumption
- **OWASP Top 10 2021:** A05:2021 — Security Misconfiguration
- **OWASP API Security Top 10:** API4:2023 — Unrestricted Resource Consumption
- **STRIDE:** Denial of Service (D)

## Internal Reference

HASI2026141-32 — Due: 2026-04-16

## References
- https://github.com/platform-mesh/kubernetes-graphql-gateway/security/advisories/GHSA-h9mw-h4qc-f5jf
- https://github.com/platform-mesh/kubernetes-graphql-gateway/commit/61509656fbab2dbf158f634d6700478ee94221ab
- https://github.com/platform-mesh/kubernetes-graphql-gateway
- https://github.com/platform-mesh/kubernetes-graphql-gateway/releases/tag/v1.2.9
