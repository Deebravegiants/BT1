### Title
Unauthenticated exposure of LOOP plugin discovery, metrics, and pprof/debug endpoints - ([File: core/web/router.go])

### Summary
`core/web/router.go` mounts `loopRoutes` on the base `api` router group, which only carries rate-limiting and session middleware — it never requires any authentication (session cookie, API token, or external-initiator credentials) before reaching the handlers.

### Finding Description
`NewRouter` registers `debugRoutes`, `healthRoutes`, `sessionRoutes`, `v2Routes`, and `loopRoutes` on the same `api` group. Every other route group that returns operational/internal data wraps its routes in `auth.Authenticate(...)`: `debugRoutes` explicitly requires a session (`auth.AuthenticateBySession`) before exposing `expvar.Handler()`, and `v2Routes` requires token/session auth for essentially all `/v2/*` node-management endpoints. [1](#0-0) [2](#0-1) 

`loopRoutes`, however, is registered directly on `api` with no auth middleware wrapper at all:
```
func loopRoutes(app chainlink.Application, r *gin.RouterGroup) {
	loopRegistry := NewLoopRegistryServer(app)
	r.GET("/discovery", ginHandlerFromHTTP(loopRegistry.discoveryHandler))
	r.GET("/plugins/:name/metrics", loopRegistry.pluginMetricHandler)
	r.GET("/plugins/:name/debug/pprof/*profile", loopRegistry.pluginPPROFHandler)
	r.POST("/plugins/:name/debug/pprof/symbol", loopRegistry.pluginPPROFPOSTSymbolHandler)
}
``` [3](#0-2) 

This is the same bug class as the Archiva advisory: an endpoint that should require authenticated/authorized access is reachable directly by an anonymous caller because the code path never runs the authorization check that sibling endpoints (`debugRoutes`, `v2Routes`) enforce. `/plugins/:name/debug/pprof/*` in particular forwards to Go's `net/http/pprof` handlers (goroutine dumps, heap profiles, full stack traces, command-line args) for each registered LOOP plugin (relayers/plugins loaded into the node), and `/discovery` and `/plugins/:name/metrics` expose internal plugin registry/metrics data — all without any credential.

### Impact Explanation
An unauthenticated network client can enumerate LOOP plugins via `/discovery`, pull runtime metrics via `/plugins/:name/metrics`, and pull full pprof profiles (goroutine stacks, heap, command-line) via `/plugins/:name/debug/pprof/*` from a production Chainlink node's web server. Stack/heap dumps and command-line output can leak internal file paths, memory contents, and process arguments, and provide a reconnaissance foothold for further attacks — directly analogous to CWE-200 (sensitive information disclosure to an unprivileged/anonymous actor) called out in the Archiva advisory.

### Likelihood Explanation
High for any deployment where the node's web server port is reachable by the caller (which is the same reachability assumption as every other `/v2` and `/debug` HTTP endpoint on this router). No credentials, tokens, or session cookies are required — a single unauthenticated HTTP GET is sufficient. I could not verify from the index whether these routes are additionally gated by network-level controls (e.g., only bound to a loopback/operator-only interface) outside of `router.go`; that would reduce likelihood if configured, but the code itself provides no application-layer authorization.

### Recommendation
Wrap `loopRoutes` registration with the same `auth.Authenticate(app.AuthenticationProvider(), auth.AuthenticateByToken, auth.AuthenticateBySession)` middleware used by `v2Routes`/`debugRoutes` (or restrict `/plugins/*/debug/pprof/*` and `/discovery` behind an admin-role check similar to `auth.RequiresAdminRole`), consistent with how `metricRoutes` for the primary node's pprof endpoints is nested only under authenticated `authv2`.

### Proof of Concept
Against a running node with `unset` credentials:
```
GET /discovery HTTP/1.1
Host: <node-host>:<web-port>

GET /plugins/<plugin-name>/metrics HTTP/1.1
Host: <node-host>:<web-port>

GET /plugins/<plugin-name>/debug/pprof/goroutine?debug=2 HTTP/1.1
Host: <node-host>:<web-port>
```
All three requests, sent with no `Cookie`, `X-API-KEY`/`X-API-SECRET`, or `Authorization` header, are routed by `loopRoutes` (`core/web/router.go:230-236`) directly to `LoopRegistryServer` handlers without passing through any `auth.Authenticate` call, unlike every comparable `/v2/*` and `/debug/*` route.

### Citations

**File:** core/web/router.go (L78-93)
```go
	api := engine.Group(
		"/",
		rateLimiter(
			rl.AuthenticatedPeriod(),
			rl.Authenticated(),
		),
		sessions.Sessions(auth.SessionName, sessionStore),
	)

	debugRoutes(app, api)
	healthRoutes(app, api)
	sessionRoutes(app, api)
	v2Routes(app, api)
	loopRoutes(app, api)

	guiAssetRoutes(engine, config.Insecure().DisableRateLimiting(), app.GetLogger())
```

**File:** core/web/router.go (L180-183)
```go
func debugRoutes(app chainlink.Application, r *gin.RouterGroup) {
	group := r.Group("/debug", auth.Authenticate(app.AuthenticationProvider(), auth.AuthenticateBySession))
	group.GET("/vars", expvar.Handler())
}
```

**File:** core/web/router.go (L230-236)
```go
func loopRoutes(app chainlink.Application, r *gin.RouterGroup) {
	loopRegistry := NewLoopRegistryServer(app)
	r.GET("/discovery", ginHandlerFromHTTP(loopRegistry.discoveryHandler))
	r.GET("/plugins/:name/metrics", loopRegistry.pluginMetricHandler)
	r.GET("/plugins/:name/debug/pprof/*profile", loopRegistry.pluginPPROFHandler)
	r.POST("/plugins/:name/debug/pprof/symbol", loopRegistry.pluginPPROFPOSTSymbolHandler)
}
```
